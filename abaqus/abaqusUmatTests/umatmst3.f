      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,STRAN,DSTRAN,
     2 TIME,DTIME,TEMP,DTEMP,PREDEF,DPRED,MATERL,NDI,NSHR,NTENS,
     3 NSTATV,PROPS,NPROPS,COORDS,DROT,PNEWDT,CELENT,
     4 DFGRD0,DFGRD1,NOEL,NPT,KSLAY,KSPT,KSTEP,KINC)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 MATERL
      DIMENSION STRESS(NTENS),STATEV(NSTATV),
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     3 PROPS(NPROPS),COORDS(3),DROT(3,3),
     4 DFGRD0(3,3),DFGRD1(3,3)
C
      DIMENSION EELAS(6),EPLAS(6),FLOW(6)
      PARAMETER (ONE=1.0D0,TWO=2.0D0,THREE=3.0D0,SIX=6.0D0)
      DATA NEWTON,TOLER/10,1.D-6/
C
C -----------------------------------------------------------
C     UMAT FOR ISOTROPIC ELASTICITY AND ISOTROPIC PLASTICITY
C     J2 FLOW THEORY
C     CAN NOT BE USED FOR PLANE STRESS
C -----------------------------------------------------------
C     PROPS(1) - E
C     PROPS(2) - NU
C     PROPS(3) - SYIELD
C     CALLS AHARD FOR CURVE OF SYIELD VS. PEEQ
C -----------------------------------------------------------
C
      IF (NDI.NE.3) THEN
         WRITE(6,1)
 1       FORMAT(//,30X,'***ERROR - THIS UMAT MAY ONLY BE USED FOR ',
     1          'ELEMENTS WITH THREE DIRECT STRESS COMPONENTS')
      ENDIF
C
C     ELASTIC PROPERTIES
C
      EMOD=PROPS(1)
      ENU=PROPS(2)
      IF(ENU.GT.0.4999.AND.ENU.LT.0.5001) ENU=0.499
      EBULK3=EMOD/(ONE-TWO*ENU)
      EG2=EMOD/(ONE+ENU)
      EG=EG2/TWO
      EG3=THREE*EG
      ELAM=(EBULK3-EG2)/THREE
C
C     ELASTIC STIFFNESS
C
      DO 20 K1=1,NTENS
        DO 10 K2=1,NTENS
           DDSDDE(K2,K1)=0.0
 10     CONTINUE
 20   CONTINUE
C
      DO 40 K1=1,NDI
        DO 30 K2=1,NDI
           DDSDDE(K2,K1)=ELAM
 30     CONTINUE
        DDSDDE(K1,K1)=EG2+ELAM
 40   CONTINUE
      DO 50 K1=NDI+1,NTENS
        DDSDDE(K1,K1)=EG
 50   CONTINUE
C
C    CALCULATE STRESS FROM ELASTIC STRAINS
C
      DO 70 K1=1,NTENS
        DO 60 K2=1,NTENS
           STRESS(K2)=STRESS(K2)+DDSDDE(K2,K1)*DSTRAN(K1)
 60     CONTINUE
 70   CONTINUE
C
C    RECOVER ELASTIC AND PLASTIC STRAINS
C
      DO 80 K1=1,NTENS
         EELAS(K1)=STATEV(K1)+DSTRAN(K1)
         EPLAS(K1)=STATEV(K1+NTENS)
 80   CONTINUE
      EQPLAS=STATEV(1+2*NTENS)
C
C    IF NO YIELD STRESS IS GIVEN, MATERIAL IS TAKEN TO BE ELASTIC
C
      IF(NPROPS.GT.2.AND.PROPS(3).GT.0.0) THEN
C
C       MISES STRESS
C
        SMISES=(STRESS(1)-STRESS(2))*(STRESS(1)-STRESS(2)) +
     1          (STRESS(2)-STRESS(3))*(STRESS(2)-STRESS(3)) +
     1          (STRESS(3)-STRESS(1))*(STRESS(3)-STRESS(1))
        DO 90 K1=NDI+1,NTENS
              SMISES=SMISES+SIX*STRESS(K1)*STRESS(K1)
 90     CONTINUE
        SMISES=SQRT(SMISES/TWO)
C
C       HARDENING CURVE, GET YIELD STRESS
C
        NVALUE=NPROPS/2-1
        CALL AHARD(SYIEL0,HARD,EQPLAS,PROPS(3),NVALUE)
C
C       DETERMINE IF ACTIVELY YIELDING
C
        IF (SMISES.GT.(1.0+TOLER)*SYIEL0) THEN
C
C         FLOW DIRECTION
C
          SHYDRO=(STRESS(1)+STRESS(2)+STRESS(3))/THREE
          ONESY=ONE/SMISES
          DO 110 K1=1,NDI
             FLOW(K1)=ONESY*(STRESS(K1)-SHYDRO)
 110      CONTINUE
          DO 120 K1=NDI+1,NTENS
             FLOW(K1)=STRESS(K1)*ONESY
 120      CONTINUE
C
C       SOLVE FOR EQUIV STRESS, NEWTON ITERATION
C
          SYIELD=SYIEL0
          DEQPL=0.0
          DO 130 KEWTON=1,NEWTON
             RHS=SMISES-EG3*DEQPL-SYIELD
             DEQPL=DEQPL+RHS/(EG3+HARD)
             CALL AHARD(SYIELD,HARD,EQPLAS+DEQPL,PROPS(3),NVALUE)
             IF(ABS(RHS).LT.TOLER*SYIEL0) GOTO 140
 130      CONTINUE
          WRITE(6,2) NEWTON
 2        FORMAT(//,30X,'***WARNING - PLASTICITY ALGORITHM DID NOT ',
     1        'CONVERGE AFTER ',I3,' ITERATIONS')
 140      CONTINUE
          EFFHRD=EG3*HARD/(EG3+HARD)
C
C       CALC STRESS AND UPDATE STRAINS
C
          DO 150 K1=1,NDI
             STRESS(K1)=FLOW(K1)*SYIELD+SHYDRO
             EPLAS(K1)=EPLAS(K1)+THREE*FLOW(K1)*DEQPL/TWO
             EELAS(K1)=EELAS(K1)-THREE*FLOW(K1)*DEQPL/TWO
 150      CONTINUE
          DO 160 K1=NDI+1,NTENS
             STRESS(K1)=FLOW(K1)*SYIELD
             EPLAS(K1)=EPLAS(K1)+THREE*FLOW(K1)*DEQPL
             EELAS(K1)=EELAS(K1)-THREE*FLOW(K1)*DEQPL
 160      CONTINUE
          EQPLAS=EQPLAS+DEQPL
          SPD=DEQPL*(SYIEL0+SYIELD)/TWO
C
C       JACOBIAN
C
          EFFG=EG*SYIELD/SMISES
          EFFG2=TWO*EFFG
          EFFG3=THREE*EFFG2/TWO
          EFFLAM=(EBULK3-EFFG2)/THREE
          DO 220 K1=1,NDI
             DO 210 K2=1,NDI
                DDSDDE(K2,K1)=EFFLAM
 210         CONTINUE
             DDSDDE(K1,K1)=EFFG2+EFFLAM
 220      CONTINUE
          DO 230 K1=NDI+1,NTENS
             DDSDDE(K1,K1)=EFFG
 230      CONTINUE
          DO 250 K1=1,NTENS
             DO 240 K2=1,NTENS
                DDSDDE(K2,K1)=DDSDDE(K2,K1)+FLOW(K2)*FLOW(K1)
     1                                       *(EFFHRD-EFFG3)
 240         CONTINUE
 250      CONTINUE
        ENDIF
      ENDIF
C
C STORE STRAINS IN STATE VARIABLE ARRAY
C
      DO 310 K1=1,NTENS
        STATEV(K1)=EELAS(K1)
        STATEV(K1+NTENS)=EPLAS(K1)
 310  CONTINUE
      STATEV(1+2*NTENS)=EQPLAS
C
      RETURN
      END
C
C
      SUBROUTINE AHARD(SYIELD,HARD,EQPLAS,TABLE,NVALUE)
C
      INCLUDE 'ABA_PARAM.INC'
      DIMENSION TABLE(2,NVALUE)
C
C    SET YIELD STRESS TO LAST VALUE OF TABLE, HARDENING TO ZERO
      SYIELD=TABLE(1,NVALUE)
      HARD=0.0
C
C   IF MORE THAN ONE ENTRY, SEARCH TABLE
C
      IF(NVALUE.GT.1) THEN
        DO 10 K1=1,NVALUE-1
           EQPL1=TABLE(2,K1+1)
           IF(EQPLAS.LT.EQPL1) THEN
             EQPL0=TABLE(2,K1)
             IF(EQPL1.LE.EQPL0) THEN
                WRITE(6,1)
 1              FORMAT(//,30X,'***ERROR - PLASTIC STRAIN MUST BE ',
     1                 'ENTERED IN ASCENDING ORDER')
                CALL XIT
              ENDIF
C
C           CURRENT YIELD STRESS AND HARDENING
C
            DEQPL=EQPL1-EQPL0
            SYIEL0=TABLE(1,K1)
            SYIEL1=TABLE(1,K1+1)
            DSYIEL=SYIEL1-SYIEL0
            HARD=DSYIEL/DEQPL
            SYIELD=SYIEL0+(EQPLAS-EQPL0)*HARD
            GOTO 20
            ENDIF
 10         CONTINUE
 20         CONTINUE
      ENDIF
      RETURN
      END
