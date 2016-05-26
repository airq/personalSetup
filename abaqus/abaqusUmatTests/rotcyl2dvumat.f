C
C User subroutine VUMAT
      subroutine vumat (
C Read only -
     *     nblock, ndir, nshr, nstatev, nfieldv, nprops, lanneal,
     *     stepTime, totalTime, dt, cmname, coordMp, charLength,
     *     props, density, strainInc, relSpinInc,
     *     tempOld, stretchOld, defgradOld, fieldOld,
     *     stressOld, stateOld, enerInternOld, enerInelasOld,
     *     tempNew, stretchNew, defgradNew, fieldNew,
C Write only -
     *     stressNew, stateNew, enerInternNew, enerInelasNew )
C
      include 'vaba_param.inc'
C
      dimension coordMp(nblock,*), charLength(nblock), props(nprops),
     1     density(nblock), strainInc(nblock,ndir+nshr),
     2     relSpinInc(nblock,nshr), tempOld(nblock),
     3     stretchOld(nblock,ndir+nshr), 
     4     defgradOld(nblock,ndir+nshr+nshr),
     5     fieldOld(nblock,nfieldv), stressOld(nblock,ndir+nshr),
     6     stateOld(nblock,nstatev), enerInternOld(nblock),
     7     enerInelasOld(nblock), tempNew(nblock),
     8     stretchNew(nblock,ndir+nshr),
     9     defgradNew(nblock,ndir+nshr+nshr),
     1     fieldNew(nblock,nfieldv),
     2     stressNew(nblock,ndir+nshr), stateNew(nblock,nstatev),
     3     enerInternNew(nblock), enerInelasNew(nblock)
C     
      character*80 cmname
      dimension intv(2)
      parameter ( zero = 0.d0, one = 1.d0, two = 2.d0, three = 3.d0,
     *     third = one / three, half = 0.5d0, twothds = two / three,
     *     op5 = 1.5d0 )
      parameter ( tempFinal = 1.d2, timeFinal = 1.d-2 )
C
C     J2 Mises Plasticity with kinematic hardening for the plane strain 
C     and axisymmetric cases. The state variables are stored as:
C            STATE(*,1) = back stress component 11
C            STATE(*,2) = back stress component 22
C            STATE(*,3) = back stress component 33
C            STATE(*,4) = back stress component 12
C            STATE(*,5) = equivalent plastic strain
C

*
*     Check that ndir=3 and nshr=1. If not, exit.
*
      intv(1) = ndir
      intv(2) = nshr
      if (ndir .ne. 3 .or. nshr .ne. 1) then
         call xplb_abqerr(1,'Subroutine VUMAT is implemented '//
     *        'only for plane strain and axisymmetric cases '//
     *        '(ndir=3 and nshr=1)',0,zero,' ')
         call xplb_abqerr(-2,'Subroutine VUMAT has been called '//
     *        'with ndir=%I and nshr=%I',intv,zero,' ')
         call xplb_exit
      end if
*     
      e      = props(1)
      xnu    = props(2)
      yield  = props(3)
      hard   = props(4)
*     
      twomu  = e / ( one + xnu )
      alamda = twomu * xnu / ( one - two * xnu )
      term   = one / ( twomu + twothds * hard )
*     
*     If stepTime equals to zero, assume the material pure elastic 
*     and use initial elastic modulus
*
      if ( stepTime .eq. zero ) then     
        do k = 1, nblock
*     Trial stress
          trace = strainInc(k,1) + strainInc(k,2) + strainInc(k,3)
          stressNew(k,1) = stressOld(k,1) 
     *         + twomu * strainInc(k,1) + alamda * trace
          stressNew(k,2) = stressOld(k,2) 
     *         + twomu * strainInc(k,2) + alamda * trace
          stressNew(k,3) = stressOld(k,3) 
     *         + twomu * strainInc(k,3) + alamda * trace
          stressNew(k,4)=stressOld(k,4) + twomu * strainInc(k,4)
        end do
      else
        const = sqrt(twothds)
        do k = 1, nblock
*     Trial stress
          trace = strainInc(k,1) + strainInc(k,2) + strainInc(k,3)
          sig1 = stressOld(k,1) + twomu*strainInc(k,1) + alamda*trace
          sig2 = stressOld(k,2) + twomu*strainInc(k,2) + alamda*trace
          sig3 = stressOld(k,3) + twomu*strainInc(k,3) + alamda*trace 
          sig4 = stressOld(k,4) + twomu*strainInc(k,4)
*     Trial stress measured from the back stress
          s1 = sig1 - stateOld(k,1)
          s2 = sig2 - stateOld(k,2)
          s3 = sig3 - stateOld(k,3)
          s4 = sig4 - stateOld(k,4)
*     Deviatoric part of trial stress measured from the back stress
          smean = third * ( s1 + s2 + s3 ) 
          ds1 = s1 - smean
          ds2 = s2 - smean
          ds3 = s3 - smean
*     Magnitude of the deviatoric trial stress difference
          dsmag = sqrt ( ds1*ds1 + ds2*ds2 + ds3*ds3 + two*s4*s4 )
*     
*     Check for yield by determining the factor for plasticity, zero for 
*     elastic, one for yield
          radius = const * yield
          facyld = zero
          if ( dsmag - radius .ge. zero ) facyld = one
*     
*     Add a protective addition factor to prevent a divide by zero 
*     when DSMAG is zero. If DSMAG is zero, we will not have exceeded 
*     the yield stress and FACYLD will be zero.
          dsmag = dsmag + ( one - facyld )
*     
*     Calculated increment in gamma ( this explicitly includes the time step)
          diff = dsmag - radius
          dgamma = facyld * term * diff
*     
*     Update equivalent plastic strain
          deqps = const * dgamma
          stateNew(k,5) = stateOld(k,5) + deqps
*     
*     Divide DGAMMA by DSMAG so that the deviatoric stresses are 
*     explicitly converted to tensors of unit magnitude in the following 
*     calculations
          dgamma = dgamma / dsmag
*     
*     Update back stress
          factor = twothds * hard * dgamma
          stateNew(k,1) = stateOld(k,1) + factor * ds1
          stateNew(k,2) = stateOld(k,2) + factor * ds2
          stateNew(k,3) = stateOld(k,3) + factor * ds3
          stateNew(k,4) = stateOld(k,4) + factor *  s4
*     
*     Update the stress
          factor = twomu * dgamma 
          stressNew(k,1) = sig1 - factor * ds1
          stressNew(k,2) = sig2 - factor * ds2
          stressNew(k,3) = sig3 - factor * ds3
          stressNew(k,4) = sig4 - factor *  s4
*     
*     Update the specific internal energy -
          stressPower = half * (
     *         ( stressOld(k,1)+stressNew(k,1) ) * strainInc(k,1) +
     *         ( stressOld(k,2)+stressNew(k,2) ) * strainInc(k,2) +
     *         ( stressOld(k,3)+stressNew(k,3) ) * strainInc(k,3) ) +
     *         ( stressOld(k,4)+stressNew(k,4) ) * strainInc(k,4)     
          enerInternNew(k) = enerInternOld(k) 
     *         + stressPower / density(k)
*     
*     Update the dissipated inelastic specific energy -
          plasticWorkInc  = dgamma * ( half * (
     *         ( stressOld(k,1)+stressNew(k,1) ) * ds1 +
     *         ( stressOld(k,2)+stressNew(k,2) ) * ds2 +
     *         ( stressOld(k,3)+stressNew(k,3) ) * ds3 ) +
     *         ( stressOld(k,4)+stressNew(k,4) ) *  s4 )     
          enerInelasNew(k) = enerInelasOld(k)
     *         + plasticWorkInc / density(k)
        end do
      end if
*     
      return
      end
