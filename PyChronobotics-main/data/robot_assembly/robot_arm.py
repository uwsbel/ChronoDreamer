# PyChrono model automatically generated using Chrono::SolidWorks add-in
# Assembly: C:\Users\sbel\Downloads\robot_arm\arm-robot-5.snapshot.1\robot\industrial robotic arm_2.SLDASM


import pychrono as chrono 
import builtins 

# Some global settings 
sphereswept_r = 0.001
chrono.ChCollisionModel.SetDefaultSuggestedEnvelope(0.003)
chrono.ChCollisionModel.SetDefaultSuggestedMargin(0.003)
chrono.ChCollisionSystemBullet.SetContactBreakingThreshold(0.002)

shapes_dir = 'robot_arm_shapes/' 

if hasattr(builtins, 'exported_system_relpath'): 
    shapes_dir = builtins.exported_system_relpath + shapes_dir 

exported_items = [] 

body_0 = chrono.ChBodyAuxRef()
body_0.SetName('SLDW_GROUND')
body_0.SetFixed(True)
exported_items.append(body_0)

# Rigid body part
body_1 = chrono.ChBodyAuxRef()
body_1.SetName('Block1-1-1^industrial robotic arm-1')
body_1.SetPos(chrono.ChVector3d(0,0,0))
body_1.SetRot(chrono.ChQuaterniond(1,0,0,0))
body_1.SetMass(6.35815492178614)
body_1.SetInertiaXX(chrono.ChVector3d(0.0325392914654591,0.0425424315333406,0.0440348359641392))
body_1.SetInertiaXY(chrono.ChVector3d(-0.00216364637365815,1.76726206797054e-06,1.19365903166813e-07))
body_1.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(0.0248065993059114,0.0914537839391301,-3.63387362797266e-06),chrono.ChQuaterniond(1,0,0,0)))
body_1.SetFixed(True)

# Visualization shape 
body_1_1_shape = chrono.ChVisualShapeModelFile() 
body_1_1_shape.SetFilename(shapes_dir +'body_1_1.obj') 
body_1_1_shape.SetColor(chrono.ChColor(0.780392156862745,0.76078431372549,0.741176470588235)) 
body_1_1_shape.SetOpacity(1) 
body_1.AddVisualShape(body_1_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_1)



# Rigid body part
body_2 = chrono.ChBodyAuxRef()
body_2.SetName('Assem5^industrial robotic arm_2-1')
body_2.SetPos(chrono.ChVector3d(0.0276760759034859,0.0539998195177369,-0.00855627230721628))
body_2.SetRot(chrono.ChQuaterniond(0.983012169382775,-0.0161133429488854,0.148485837422196,-0.10667422889063))
body_2.SetMass(9.52797372577916)
body_2.SetInertiaXX(chrono.ChVector3d(0.0588689020098606,0.173142042450058,0.164886435976486))
body_2.SetInertiaXY(chrono.ChVector3d(-0.0093252428902958,-0.0270187966164158,-0.0056785838459094))
body_2.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.401489695264453,0.533180589448216,-0.00882147290792453),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_2_1_shape = chrono.ChVisualShapeModelFile() 
body_2_1_shape.SetFilename(shapes_dir +'body_2_1.obj') 
body_2.AddVisualShape(body_2_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.22048352578521,0.223688426635073,-2.25514051876985E-17), chrono.ChQuaterniond(0.991366672698128,-2.34163666743667E-17,2.49002232307443E-17,0.13111872583061)))

# Visualization shape 
body_2_2_shape = chrono.ChVisualShapeModelFile() 
body_2_2_shape.SetFilename(shapes_dir +'body_2_2.obj') 
body_2.AddVisualShape(body_2_2_shape, chrono.ChFramed(chrono.ChVector3d(-0.124922519257827,-0.0650596762319682,-5.20417042793042E-18), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_2_3_shape = chrono.ChVisualShapeModelFile() 
body_2_3_shape.SetFilename(shapes_dir +'body_2_3.obj') 
body_2.AddVisualShape(body_2_3_shape, chrono.ChFramed(chrono.ChVector3d(-0.220483525785213,0.223688426635067,-1.73472347597681E-18), chrono.ChQuaterniond(0.991366672698128,-1.63375968840893E-17,-2.160819952466E-18,0.13111872583061)))

# Visualization shape 
body_2_4_shape = chrono.ChVisualShapeModelFile() 
body_2_4_shape.SetFilename(shapes_dir +'body_2_4.obj') 
body_2.AddVisualShape(body_2_4_shape, chrono.ChFramed(chrono.ChVector3d(0.453436171818078,-0.0650596762319681,5.20417042793042E-18), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_2_5_shape = chrono.ChVisualShapeModelFile() 
body_2_5_shape.SetFilename(shapes_dir +'body_2_5.obj') 
body_2.AddVisualShape(body_2_5_shape, chrono.ChFramed(chrono.ChVector3d(-0.543321144291398,0.619181847628244,0.015), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_2_5_shape = chrono.ChVisualShapeModelFile() 
body_2_5_shape.SetFilename(shapes_dir +'body_2_5.obj') 
body_2.AddVisualShape(body_2_5_shape, chrono.ChFramed(chrono.ChVector3d(-0.543321144291398,0.619181847628244,-0.015), chrono.ChQuaterniond(0.973742326368847,-5.3445046877413E-18,-0.227652985567477,-9.79825859419238E-18)))

# Visualization shape 
body_2_7_shape = chrono.ChVisualShapeModelFile() 
body_2_7_shape.SetFilename(shapes_dir +'body_2_7.obj') 
body_2.AddVisualShape(body_2_7_shape, chrono.ChFramed(chrono.ChVector3d(-0.0791099203362491,-0.0726105246150223,3.98986399474666E-17), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_2_8_shape = chrono.ChVisualShapeModelFile() 
body_2_8_shape.SetFilename(shapes_dir +'body_2_8.obj') 
body_2.AddVisualShape(body_2_8_shape, chrono.ChFramed(chrono.ChVector3d(-0.0767998869238415,-0.084411986699126,1.73472347597681E-18), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_2)



# Rigid body part
body_3 = chrono.ChBodyAuxRef()
body_3.SetName('mob clap-2')
body_3.SetPos(chrono.ChVector3d(0.876189005718355,0.222073591032561,0.0887301370591297))
body_3.SetRot(chrono.ChQuaterniond(0.399391995646576,-0.576515611725721,0.644285929935965,-0.304977743018261))
body_3.SetMass(0.0433433495958865)
body_3.SetInertiaXX(chrono.ChVector3d(4.46317845422771e-05,1.52134237990613e-05,3.76269078878132e-05))
body_3.SetInertiaXY(chrono.ChVector3d(5.07661738539662e-06,-8.73801640236105e-07,8.75340806355403e-06))
body_3.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.706700955784656,0.742160345409192,-1.168128446535),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_3_1_shape = chrono.ChVisualShapeModelFile() 
body_3_1_shape.SetFilename(shapes_dir +'body_3_1.obj') 
body_3.AddVisualShape(body_3_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_3)



# Rigid body part
body_4 = chrono.ChBodyAuxRef()
body_4.SetName('Assem3^industrial robotic arm_2-1')
body_4.SetPos(chrono.ChVector3d(-0.638896886867162,-0.0747288252137868,-0.170220956677891))
body_4.SetRot(chrono.ChQuaterniond(0.703335134788063,0.323124173413111,-0.384858621417213,-0.502786533480753))
body_4.SetMass(0.279459438756902)
body_4.SetInertiaXX(chrono.ChVector3d(0.000329648812392015,0.000199465939768669,0.000297727352568862))
body_4.SetInertiaXY(chrono.ChVector3d(-3.51328039487827e-05,-2.80585442706635e-05,-8.75400841456991e-05))
body_4.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.838978590742122,0.610910913034362,-1.72038958430793e-05),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_4_1_shape = chrono.ChVisualShapeModelFile() 
body_4_1_shape.SetFilename(shapes_dir +'body_4_1.obj') 
body_4_1_shape.SetColor(chrono.ChColor(0.498039215686275,0.498039215686275,0.498039215686275)) 
body_4_1_shape.SetOpacity(1) 
body_4.AddVisualShape(body_4_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.835851887877873,0.610059280422067,2.22044604925031E-16), chrono.ChQuaterniond(0.700420252077117,-0.0970127335983712,-0.700420252077116,-0.0970127335983712)))

# Visualization shape 
body_4_2_shape = chrono.ChVisualShapeModelFile() 
body_4_2_shape.SetFilename(shapes_dir +'body_4_2.obj') 
body_4.AddVisualShape(body_4_2_shape, chrono.ChFramed(chrono.ChVector3d(-0.854617793180415,0.615359355721157,2.22044604925031E-16), chrono.ChQuaterniond(0.700420252077116,-0.0970127335983713,-0.700420252077117,-0.0970127335983711)))

# Visualization shape 
body_4_3_shape = chrono.ChVisualShapeModelFile() 
body_4_3_shape.SetFilename(shapes_dir +'body_4_3.obj') 
body_4.AddVisualShape(body_4_3_shape, chrono.ChFramed(chrono.ChVector3d(-0.850661722094262,0.601772615804558,0.0140042868237457), chrono.ChQuaterniond(0.725818635283479,-9.56009334370031E-18,-1.43401400155505E-17,-0.687886116065173)))

# Visualization shape 
body_4_4_shape = chrono.ChVisualShapeModelFile() 
body_4_4_shape.SetFilename(shapes_dir +'body_4_4.obj') 
body_4.AddVisualShape(body_4_4_shape, chrono.ChFramed(chrono.ChVector3d(-0.81660480551629,0.604623305756335,1.66533453693773E-16), chrono.ChQuaterniond(0.700420252077117,-0.0970127335983713,-0.700420252077116,-0.0970127335983711)))

# Visualization shape 
body_4_3_shape = chrono.ChVisualShapeModelFile() 
body_4_3_shape.SetFilename(shapes_dir +'body_4_3.obj') 
body_4.AddVisualShape(body_4_3_shape, chrono.ChFramed(chrono.ChVector3d(-0.844138552495382,0.624869114638456,-0.0690042868237457), chrono.ChQuaterniond(0.959554578038372,-2.66329896480669E-17,7.81382365816216E-18,-0.281522666521903)))

exported_items.append(body_4)



# Rigid body part
body_5 = chrono.ChBodyAuxRef()
body_5.SetName('Assem7^industrial robotic arm_2-1')
body_5.SetPos(chrono.ChVector3d(0,0,0))
body_5.SetRot(chrono.ChQuaterniond(0.988783250396183,-7.18096349960828e-17,0.149357570065797,-8.16534013897043e-17))
body_5.SetMass(6.1917518054616)
body_5.SetInertiaXX(chrono.ChVector3d(0.0356647440050639,0.0439097014372601,0.0331490876174919))
body_5.SetInertiaXY(chrono.ChVector3d(0.00412535793623527,-0.000635694490889194,0.00282779435004725))
body_5.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.0470727759918959,0.278321349820769,-0.0152777759103433),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_5_1_shape = chrono.ChVisualShapeModelFile() 
body_5_1_shape.SetFilename(shapes_dir +'body_5_1.obj') 
body_5_1_shape.SetColor(chrono.ChColor(0.647058823529412,0.619607843137255,0.6)) 
body_5_1_shape.SetOpacity(1) 
body_5.AddVisualShape(body_5_1_shape, chrono.ChFramed(chrono.ChVector3d(4.62223186652937E-33,0.150481497931565,3.08148791101958E-33), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_2_3_shape = chrono.ChVisualShapeModelFile() 
body_2_3_shape.SetFilename(shapes_dir +'body_2_3.obj') 
body_5.AddVisualShape(body_2_3_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_2_1_shape = chrono.ChVisualShapeModelFile() 
body_2_1_shape.SetFilename(shapes_dir +'body_2_1.obj') 
body_5.AddVisualShape(body_2_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_5_4_shape = chrono.ChVisualShapeModelFile() 
body_5_4_shape.SetFilename(shapes_dir +'body_5_4.obj') 
body_5.AddVisualShape(body_5_4_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_5)



# Rigid body part
body_6 = chrono.ChBodyAuxRef()
body_6.SetName('Assem4^industrial robotic arm_2-1')
body_6.SetPos(chrono.ChVector3d(-0.80371849939616,-0.0942228136342629,0.248475772474348))
body_6.SetRot(chrono.ChQuaterniond(0.808664361522975,-0.0859476266491804,0.122150273062865,-0.568994083156126))
body_6.SetMass(0.690905359894318)
body_6.SetInertiaXX(chrono.ChVector3d(0.00191218043044322,0.00133158554328127,0.00252351271142892))
body_6.SetInertiaXY(chrono.ChVector3d(-0.000738171610470456,-0.0002976897173575,-0.000475166340649388))
body_6.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.731419039863803,0.584005934529981,-3.70207795692631e-05),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_6_1_shape = chrono.ChVisualShapeModelFile() 
body_6_1_shape.SetFilename(shapes_dir +'body_6_1.obj') 
body_6_1_shape.SetColor(chrono.ChColor(0.647058823529412,0.619607843137255,0.588235294117647)) 
body_6_1_shape.SetOpacity(1) 
body_6.AddVisualShape(body_6_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.689574061929817,0.568745872962511,2.77555756156289E-17), chrono.ChQuaterniond(-4.2906456342278E-17,0.137196723577704,0.99054381984824,1.4010271458703E-17)))

# Visualization shape 
body_6_2_shape = chrono.ChVisualShapeModelFile() 
body_6_2_shape.SetFilename(shapes_dir +'body_6_2.obj') 
body_6.AddVisualShape(body_6_2_shape, chrono.ChFramed(chrono.ChVector3d(-0.778110640793093,0.593751356424883,2.77555756156289E-17), chrono.ChQuaterniond(0.700420252077117,-0.0970127335983713,-0.700420252077117,-0.0970127335983712)))

exported_items.append(body_6)



# Rigid body part
body_7 = chrono.ChBodyAuxRef()
body_7.SetName('mob clap-1')
body_7.SetPos(chrono.ChVector3d(-1.84149583261998,0.039466186495734,0.214244467128427))
body_7.SetRot(chrono.ChQuaterniond(0.674612048750725,0.343805844779586,-0.366500929082672,-0.540715446198167))
body_7.SetMass(0.0433433495958865)
body_7.SetInertiaXX(chrono.ChVector3d(3.84204466773788e-05,2.14247616639596e-05,3.76269078878132e-05))
body_7.SetInertiaXY(chrono.ChVector3d(-1.30352868788288e-05,3.6661215118331e-06,7.9965764608391e-06))
body_7.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.706700955784656,0.742160345409192,-1.168128446535),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_3_1_shape = chrono.ChVisualShapeModelFile() 
body_3_1_shape.SetFilename(shapes_dir +'body_3_1.obj') 
body_7.AddVisualShape(body_3_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_7)



# Rigid body part
body_8 = chrono.ChBodyAuxRef()
body_8.SetName('Assem6^industrial robotic arm_2-1')
body_8.SetPos(chrono.ChVector3d(-0.105295069842693,-0.0128019977144107,0.0325527828917216))
body_8.SetRot(chrono.ChQuaterniond(0.972554964317149,-0.0269487553004896,0.146906256924998,-0.178407280249742))
body_8.SetMass(2.51123451031168)
body_8.SetInertiaXX(chrono.ChVector3d(0.0128915890005373,0.0434644435976513,0.0503890475147785))
body_8.SetInertiaXY(chrono.ChVector3d(0.0170632350479128,-0.00964736194222884,0.00391309447589583))
body_8.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.217022834717109,0.414372371508091,0.123094501311852),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_8_1_shape = chrono.ChVisualShapeModelFile() 
body_8_1_shape.SetFilename(shapes_dir +'body_8_1.obj') 
body_8.AddVisualShape(body_8_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.227161101767316,0.423979776782739,3.46944695195361E-18), chrono.ChQuaterniond(0.918653832476948,8.15811074440841E-18,3.37216761790394E-17,0.395063458289191)))

# Visualization shape 
body_8_2_shape = chrono.ChVisualShapeModelFile() 
body_8_2_shape.SetFilename(shapes_dir +'body_8_2.obj') 
body_8.AddVisualShape(body_8_2_shape, chrono.ChFramed(chrono.ChVector3d(0.0593547632575067,0.0212044641075161,0.000753926210741272), chrono.ChQuaterniond(0.99251448470166,-5.24342012952561E-18,0,0.122126973504618)))

exported_items.append(body_8)



# Rigid body part
body_9 = chrono.ChBodyAuxRef()
body_9.SetName('Mod clmp ND-1')
body_9.SetPos(chrono.ChVector3d(-0.523015769627327,0.989845753772525,0.159649235759544))
body_9.SetRot(chrono.ChQuaterniond(0.594527369512293,-0.336887751059097,-0.372869994917008,0.627703605993886))
body_9.SetMass(0.0052993130677972)
body_9.SetInertiaXX(chrono.ChVector3d(1.02538841884199e-06,1.03984572838099e-06,4.95989314486004e-07))
body_9.SetInertiaXY(chrono.ChVector3d(-2.78088943311363e-08,-4.22749420700088e-08,-4.13324944515958e-07))
body_9.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(0.000338388209168651,-4.63200996498398e-18,0.00149280144822819),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_9_1_shape = chrono.ChVisualShapeModelFile() 
body_9_1_shape.SetFilename(shapes_dir +'body_9_1.obj') 
body_9.AddVisualShape(body_9_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_9)



# Rigid body part
body_10 = chrono.ChBodyAuxRef()
body_10.SetName('Mod clmp ND-2')
body_10.SetPos(chrono.ChVector3d(-0.555942374507091,0.987279198085864,0.178461549644874))
body_10.SetRot(chrono.ChQuaterniond(0.336887751059107,0.594527369512275,0.627703605993903,0.372869994917))
body_10.SetMass(0.0052993130677972)
body_10.SetInertiaXX(chrono.ChVector3d(1.02538841884199e-06,1.03984572838099e-06,4.95989314486005e-07))
body_10.SetInertiaXY(chrono.ChVector3d(2.78088943311362e-08,4.22749420700326e-08,-4.13324944515956e-07))
body_10.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(0.000338388209168651,-4.63200996498398e-18,0.00149280144822819),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_9_1_shape = chrono.ChVisualShapeModelFile() 
body_9_1_shape.SetFilename(shapes_dir +'body_9_1.obj') 
body_10.AddVisualShape(body_9_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_10)




# Mate constraint: Distance1 [MateDistanceDim] type:5 align:1 flip:False
#   Entity 0: C::E name: body_5 , SW name: Assem7^industrial robotic arm_2-1/A02-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_1 , SW name: Block1-1-1^industrial robotic arm-1 ,  SW ref.type:2 (2)
link_1 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(2.67446615619253e-17,0.191,-3.17822922455789e-17)
cB = chrono.ChVector3d(0,0.185,0)
dA = chrono.ChVector3d(-1.40024406083379e-16,-1,1.66399435840727e-16)
dB = chrono.ChVector3d(0,1,0)
link_1.Initialize(body_5,body_1,False,cA,cB,dB)
link_1.SetDistance(0.00599999999999998)
link_1.SetName("Distance1")
exported_items.append(link_1)

link_2 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(2.67446615619253e-17,0.191,-3.17822922455789e-17)
dA = chrono.ChVector3d(-1.40024406083379e-16,-1,1.66399435840727e-16)
cB = chrono.ChVector3d(0,0.185,0)
dB = chrono.ChVector3d(0,1,0)
link_2.SetFlipped(True)
link_2.Initialize(body_5,body_1,False,cA,cB,dA,dB)
link_2.SetName("Distance1")
exported_items.append(link_2)


# Mate constraint: Concentric1 [MateConcentric] type:1 align:1 flip:False
#   Entity 0: C::E name: body_1 , SW name: Block1-1-1^industrial robotic arm-1 ,  SW ref.type:1 (1)
#   Entity 1: C::E name: body_5 , SW name: Assem7^industrial robotic arm_2-1/A02-1 ,  SW ref.type:1 (1)
link_3 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(0,0.184,0)
dA = chrono.ChVector3d(0,-1,0)
cB = chrono.ChVector3d(2.68846859680087e-17,0.192,-3.19486916814196e-17)
dB = chrono.ChVector3d(1.40024406083379e-16,1,-1.66399435840727e-16)
link_3.SetFlipped(True)
link_3.Initialize(body_1,body_5,False,cA,cB,dA,dB)
link_3.SetName("Concentric1")
exported_items.append(link_3)

link_4 = chrono.ChLinkMateGeneric()
link_4.SetConstrainedCoords(True, True, False, False, False, False)
cA = chrono.ChVector3d(0,0.184,0)
cB = chrono.ChVector3d(2.68846859680087e-17,0.192,-3.19486916814196e-17)
dA = chrono.ChVector3d(0,-1,0)
dB = chrono.ChVector3d(1.40024406083379e-16,1,-1.66399435840727e-16)
link_4.Initialize(body_1,body_5,False,cA,cB,dA,dB)
link_4.SetName("Concentric1")
exported_items.append(link_4)


# Mate constraint: Distance2 [MateDistanceDim] type:5 align:1 flip:False
#   Entity 0: C::E name: body_5 , SW name: Assem7^industrial robotic arm_2-1/servo cap 2-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_8 , SW name: Assem6^industrial robotic arm_2-1/A03-1 ,  SW ref.type:2 (2)
link_5 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(0.0265828074481682,0.294,0.0859846169275272)
cB = chrono.ChVector3d(-0.058515715897754,0.293999999999984,0.115433578273279)
dA = chrono.ChVector3d(0.295364527201869,1.17617221364034e-16,0.955384632528081)
dB = chrono.ChVector3d(-0.295364527201868,-1.04083408558608e-15,-0.955384632528081)
link_5.Initialize(body_5,body_8,False,cA,cB,dB)
link_5.SetDistance(0.00300000000000028)
link_5.SetName("Distance2")
exported_items.append(link_5)

link_6 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(0.0265828074481682,0.294,0.0859846169275272)
dA = chrono.ChVector3d(0.295364527201869,1.17617221364034e-16,0.955384632528081)
cB = chrono.ChVector3d(-0.058515715897754,0.293999999999984,0.115433578273279)
dB = chrono.ChVector3d(-0.295364527201868,-1.04083408558608e-15,-0.955384632528081)
link_6.SetFlipped(True)
link_6.Initialize(body_5,body_8,False,cA,cB,dA,dB)
link_6.SetName("Distance2")
exported_items.append(link_6)


# Mate constraint: Concentric4 [MateConcentric] type:1 align:1 flip:False
#   Entity 0: C::E name: body_5 , SW name: Assem7^industrial robotic arm_2-1/servo cap 2-1 ,  SW ref.type:1 (1)
#   Entity 1: C::E name: body_8 , SW name: Assem6^industrial robotic arm_2-1/A03-1 ,  SW ref.type:1 (1)
link_7 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.055562070625735,0.294000000000001,0.124987424598561)
dA = chrono.ChVector3d(0.295364527201869,1.17617221364034e-16,0.955384632528081)
cB = chrono.ChVector3d(-0.0555620706257353,0.293999999999984,0.124987424598559)
dB = chrono.ChVector3d(-0.295364527201868,-1.04083408558608e-15,-0.955384632528081)
link_7.SetFlipped(True)
link_7.Initialize(body_5,body_8,False,cA,cB,dA,dB)
link_7.SetName("Concentric4")
exported_items.append(link_7)

link_8 = chrono.ChLinkMateGeneric()
link_8.SetConstrainedCoords(True, True, False, False, False, False)
cA = chrono.ChVector3d(-0.055562070625735,0.294000000000001,0.124987424598561)
cB = chrono.ChVector3d(-0.0555620706257353,0.293999999999984,0.124987424598559)
dA = chrono.ChVector3d(0.295364527201869,1.17617221364034e-16,0.955384632528081)
dB = chrono.ChVector3d(-0.295364527201868,-1.04083408558608e-15,-0.955384632528081)
link_8.Initialize(body_5,body_8,False,cA,cB,dA,dB)
link_8.SetName("Concentric4")
exported_items.append(link_8)


# Mate constraint: Distance4 [MateDistanceDim] type:5 align:1 flip:False
#   Entity 0: C::E name: body_2 , SW name: Assem5^industrial robotic arm_2-1/servo cap 2-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_8 , SW name: Assem6^industrial robotic arm_2-1/A03-1 ,  SW ref.type:2 (2)
link_9 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.118783792016917,0.613455008815629,0.130925822239077)
cB = chrono.ChVector3d(-0.203788147821751,0.609244071241764,0.160345670963272)
dA = chrono.ChVector3d(0.295364527201867,5.87203896618149e-16,0.955384632528082)
dB = chrono.ChVector3d(-0.295364527201868,-1.04083408558608e-15,-0.955384632528081)
link_9.Initialize(body_2,body_8,False,cA,cB,dB)
link_9.SetDistance(0.003)
link_9.SetName("Distance4")
exported_items.append(link_9)

link_10 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.118783792016917,0.613455008815629,0.130925822239077)
dA = chrono.ChVector3d(0.295364527201867,5.87203896618149e-16,0.955384632528082)
cB = chrono.ChVector3d(-0.203788147821751,0.609244071241764,0.160345670963272)
dB = chrono.ChVector3d(-0.295364527201868,-1.04083408558608e-15,-0.955384632528081)
link_10.SetFlipped(True)
link_10.Initialize(body_2,body_8,False,cA,cB,dA,dB)
link_10.SetName("Distance4")
exported_items.append(link_10)


# Mate constraint: Concentric5 [MateConcentric] type:1 align:1 flip:False
#   Entity 0: C::E name: body_8 , SW name: Assem6^industrial robotic arm_2-1/A03-1 ,  SW ref.type:1 (1)
#   Entity 1: C::E name: body_2 , SW name: Assem5^industrial robotic arm_2-1/servo cap 2-1 ,  SW ref.type:1 (1)
link_11 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.203788147821751,0.609244071241764,0.160345670963272)
dA = chrono.ChVector3d(-0.295364527201868,-1.04083408558608e-15,-0.955384632528081)
cB = chrono.ChVector3d(-0.200834502549733,0.609244071241778,0.16989951728855)
dB = chrono.ChVector3d(0.295364527201867,5.87203896618149e-16,0.955384632528082)
link_11.SetFlipped(True)
link_11.Initialize(body_8,body_2,False,cA,cB,dA,dB)
link_11.SetName("Concentric5")
exported_items.append(link_11)

link_12 = chrono.ChLinkMateGeneric()
link_12.SetConstrainedCoords(True, True, False, False, False, False)
cA = chrono.ChVector3d(-0.203788147821751,0.609244071241764,0.160345670963272)
cB = chrono.ChVector3d(-0.200834502549733,0.609244071241778,0.16989951728855)
dA = chrono.ChVector3d(-0.295364527201868,-1.04083408558608e-15,-0.955384632528081)
dB = chrono.ChVector3d(0.295364527201867,5.87203896618149e-16,0.955384632528082)
link_12.Initialize(body_8,body_2,False,cA,cB,dA,dB)
link_12.SetName("Concentric5")
exported_items.append(link_12)


# Mate constraint: Coincident7 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_7 , SW name: mob clap-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_10 , SW name: Mod clmp ND-2 ,  SW ref.type:2 (2)
link_13 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.558128567345211,0.992004644381879,0.185381861644923)
cB = chrono.ChVector3d(-0.558561714418597,0.991970881529977,0.185629336254996)
dA = chrono.ChVector3d(-0.495143279359832,-0.0150103475828205,-0.868681657668812)
dB = chrono.ChVector3d(0.495143279359832,0.0150103475828228,0.868681657668812)
link_13.Initialize(body_7,body_10,False,cA,cB,dB)
link_13.SetDistance(0)
link_13.SetName("Coincident7")
exported_items.append(link_13)

link_14 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.558128567345211,0.992004644381879,0.185381861644923)
dA = chrono.ChVector3d(-0.495143279359832,-0.0150103475828205,-0.868681657668812)
cB = chrono.ChVector3d(-0.558561714418597,0.991970881529977,0.185629336254996)
dB = chrono.ChVector3d(0.495143279359832,0.0150103475828228,0.868681657668812)
link_14.SetFlipped(True)
link_14.Initialize(body_7,body_10,False,cA,cB,dA,dB)
link_14.SetName("Coincident7")
exported_items.append(link_14)


# Mate constraint: Coincident9 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_7 , SW name: mob clap-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_10 , SW name: Mod clmp ND-2 ,  SW ref.type:2 (2)
link_15 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.558789444346954,1.00198069053648,0.185586176866785)
cB = chrono.ChVector3d(-0.564174024213939,1.00179682420875,0.177146834900169)
dA = chrono.ChVector3d(0.0660877001743006,-0.997604615459867,-0.0204315221861639)
dB = chrono.ChVector3d(-0.0660877001743035,0.997604615459866,0.0204315221861628)
link_15.Initialize(body_7,body_10,False,cA,cB,dB)
link_15.SetDistance(0)
link_15.SetName("Coincident9")
exported_items.append(link_15)

link_16 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.558789444346954,1.00198069053648,0.185586176866785)
dA = chrono.ChVector3d(0.0660877001743006,-0.997604615459867,-0.0204315221861639)
cB = chrono.ChVector3d(-0.564174024213939,1.00179682420875,0.177146834900169)
dB = chrono.ChVector3d(-0.0660877001743035,0.997604615459866,0.0204315221861628)
link_16.SetFlipped(True)
link_16.Initialize(body_7,body_10,False,cA,cB,dA,dB)
link_16.SetName("Coincident9")
exported_items.append(link_16)


# Mate constraint: Coincident10 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_7 , SW name: mob clap-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_10 , SW name: Mod clmp ND-2 ,  SW ref.type:2 (2)
link_17 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.531880042722885,0.128493385435956,0.103413327022648)
cB = chrono.ChVector3d(-0.555942374507091,0.987279198085864,0.178461549644874)
dA = chrono.ChVector3d(0.866294146806074,0.0675257038364953,-0.494949220153868)
dB = chrono.ChVector3d(-0.866294146806074,-0.0675257038365032,0.494949220153868)
link_17.Initialize(body_7,body_10,False,cA,cB,dB)
link_17.SetDistance(0)
link_17.SetName("Coincident10")
exported_items.append(link_17)

link_18 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.531880042722885,0.128493385435956,0.103413327022648)
dA = chrono.ChVector3d(0.866294146806074,0.0675257038364953,-0.494949220153868)
cB = chrono.ChVector3d(-0.555942374507091,0.987279198085864,0.178461549644874)
dB = chrono.ChVector3d(-0.866294146806074,-0.0675257038365032,0.494949220153868)
link_18.SetFlipped(True)
link_18.Initialize(body_7,body_10,False,cA,cB,dA,dB)
link_18.SetName("Coincident10")
exported_items.append(link_18)


# Mate constraint: Coincident11 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_4 , SW name: Assem3^industrial robotic arm_2-1/Mod SL ND-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_7 , SW name: mob clap-1 ,  SW ref.type:2 (2)
link_19 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.460412167457301,0.929348284794133,0.117528322398079)
cB = chrono.ChVector3d(-0.606819591918085,0.917936151375312,0.201176862363817)
dA = chrono.ChVector3d(-0.495143279359837,-0.0150103475827914,-0.868681657668809)
dB = chrono.ChVector3d(0.495143279359832,0.0150103475828114,0.868681657668812)
link_19.Initialize(body_4,body_7,False,cA,cB,dB)
link_19.SetDistance(0)
link_19.SetName("Coincident11")
exported_items.append(link_19)

link_20 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.460412167457301,0.929348284794133,0.117528322398079)
dA = chrono.ChVector3d(-0.495143279359837,-0.0150103475827914,-0.868681657668809)
cB = chrono.ChVector3d(-0.606819591918085,0.917936151375312,0.201176862363817)
dB = chrono.ChVector3d(0.495143279359832,0.0150103475828114,0.868681657668812)
link_20.SetFlipped(True)
link_20.Initialize(body_4,body_7,False,cA,cB,dA,dB)
link_20.SetName("Coincident11")
exported_items.append(link_20)


# Mate constraint: Coincident12 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_4 , SW name: Assem3^industrial robotic arm_2-1/Mod SL ND-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_7 , SW name: mob clap-1 ,  SW ref.type:2 (2)
link_21 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.52708831501597,0.932965748595652,0.162953417563718)
cB = chrono.ChVector3d(-0.600231061497389,0.927075754264413,0.213955473178496)
dA = chrono.ChVector3d(-0.066087700174286,0.997604615459867,0.0204315221861869)
dB = chrono.ChVector3d(0.0660877001742867,-0.997604615459867,-0.0204315221861875)
link_21.Initialize(body_4,body_7,False,cA,cB,dB)
link_21.SetDistance(0)
link_21.SetName("Coincident12")
exported_items.append(link_21)

link_22 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.52708831501597,0.932965748595652,0.162953417563718)
dA = chrono.ChVector3d(-0.066087700174286,0.997604615459867,0.0204315221861869)
cB = chrono.ChVector3d(-0.600231061497389,0.927075754264413,0.213955473178496)
dB = chrono.ChVector3d(0.0660877001742867,-0.997604615459867,-0.0204315221861875)
link_22.SetFlipped(True)
link_22.Initialize(body_4,body_7,False,cA,cB,dA,dB)
link_22.SetName("Coincident12")
exported_items.append(link_22)


# Mate constraint: Coincident14 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_3 , SW name: mob clap-2 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_9 , SW name: Mod clmp ND-1 ,  SW ref.type:2 (2)
link_23 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.521490453791001,0.995096353631081,0.152933238981397)
cB = chrono.ChVector3d(-0.521057306717564,0.995130116483011,0.152685764371285)
dA = chrono.ChVector3d(0.495143279359834,0.015010347582767,0.868681657668811)
dB = chrono.ChVector3d(-0.495143279359835,-0.0150103475827675,-0.868681657668811)
link_23.Initialize(body_3,body_9,False,cA,cB,dB)
link_23.SetDistance(0)
link_23.SetName("Coincident14")
exported_items.append(link_23)

link_24 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.521490453791001,0.995096353631081,0.152933238981397)
dA = chrono.ChVector3d(0.495143279359834,0.015010347582767,0.868681657668811)
cB = chrono.ChVector3d(-0.521057306717564,0.995130116483011,0.152685764371285)
dB = chrono.ChVector3d(-0.495143279359835,-0.0150103475827675,-0.868681657668811)
link_24.SetFlipped(True)
link_24.Initialize(body_3,body_9,False,cA,cB,dA,dB)
link_24.SetName("Coincident14")
exported_items.append(link_24)


# Mate constraint: Coincident15 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_3 , SW name: mob clap-2 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_9 , SW name: Mod clmp ND-1 ,  SW ref.type:2 (2)
link_25 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.522151330792744,1.00507239978568,0.153137554203259)
cB = chrono.ChVector3d(-0.516766750925708,1.00525626611344,0.161576896169835)
dA = chrono.ChVector3d(0.066087700174273,-0.997604615459867,-0.0204315221862097)
dB = chrono.ChVector3d(-0.0660877001742746,0.997604615459867,0.0204315221862102)
link_25.Initialize(body_3,body_9,False,cA,cB,dB)
link_25.SetDistance(0)
link_25.SetName("Coincident15")
exported_items.append(link_25)

link_26 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.522151330792744,1.00507239978568,0.153137554203259)
dA = chrono.ChVector3d(0.066087700174273,-0.997604615459867,-0.0204315221862097)
cB = chrono.ChVector3d(-0.516766750925708,1.00525626611344,0.161576896169835)
dB = chrono.ChVector3d(-0.0660877001742746,0.997604615459867,0.0204315221862102)
link_26.SetFlipped(True)
link_26.Initialize(body_3,body_9,False,cA,cB,dA,dB)
link_26.SetName("Coincident15")
exported_items.append(link_26)


# Mate constraint: Coincident16 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_3 , SW name: mob clap-2 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_9 , SW name: Mod clmp ND-1 ,  SW ref.type:2 (2)
link_27 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.433426784178743,0.133046392092352,0.199561277164907)
cB = chrono.ChVector3d(-0.523015769627327,0.989845753772525,0.159649235759544)
dA = chrono.ChVector3d(-0.866294146806074,-0.0675257038365059,0.494949220153866)
dB = chrono.ChVector3d(0.866294146806074,0.0675257038365016,-0.494949220153867)
link_27.Initialize(body_3,body_9,False,cA,cB,dB)
link_27.SetDistance(0)
link_27.SetName("Coincident16")
exported_items.append(link_27)

link_28 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.433426784178743,0.133046392092352,0.199561277164907)
dA = chrono.ChVector3d(-0.866294146806074,-0.0675257038365059,0.494949220153866)
cB = chrono.ChVector3d(-0.523015769627327,0.989845753772525,0.159649235759544)
dB = chrono.ChVector3d(0.866294146806074,0.0675257038365016,-0.494949220153867)
link_28.SetFlipped(True)
link_28.Initialize(body_3,body_9,False,cA,cB,dA,dB)
link_28.SetName("Coincident16")
exported_items.append(link_28)


# Mate constraint: Coincident17 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_4 , SW name: Assem3^industrial robotic arm_2-1/Mod SL ND-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_3 , SW name: mob clap-2 ,  SW ref.type:2 (2)
link_29 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.52708831501597,0.932965748595652,0.162953417563718)
cB = chrono.ChVector3d(-0.471271451470682,0.937505228850133,0.121850346352032)
dA = chrono.ChVector3d(-0.066087700174286,0.997604615459867,0.0204315221861869)
dB = chrono.ChVector3d(0.0660877001742869,-0.997604615459867,-0.0204315221861861)
link_29.Initialize(body_4,body_3,False,cA,cB,dB)
link_29.SetDistance(0)
link_29.SetName("Coincident17")
exported_items.append(link_29)

link_30 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.52708831501597,0.932965748595652,0.162953417563718)
dA = chrono.ChVector3d(-0.066087700174286,0.997604615459867,0.0204315221861869)
cB = chrono.ChVector3d(-0.471271451470682,0.937505228850133,0.121850346352032)
dB = chrono.ChVector3d(0.0660877001742869,-0.997604615459867,-0.0204315221861861)
link_30.SetFlipped(True)
link_30.Initialize(body_4,body_3,False,cA,cB,dA,dB)
link_30.SetName("Coincident17")
exported_items.append(link_30)


# Mate constraint: Coincident18 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_4 , SW name: Assem3^industrial robotic arm_2-1/Mod SL ND-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_3 , SW name: mob clap-2 ,  SW ref.type:2 (2)
link_31 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.453975304825623,0.92954341931271,0.128821183947774)
cB = chrono.ChVector3d(-0.463500826789943,0.928800926040933,0.134263503609747)
dA = chrono.ChVector3d(0.495143279359837,0.0150103475827935,0.868681657668809)
dB = chrono.ChVector3d(-0.495143279359834,-0.0150103475827762,-0.868681657668812)
link_31.Initialize(body_4,body_3,False,cA,cB,dB)
link_31.SetDistance(0)
link_31.SetName("Coincident18")
exported_items.append(link_31)

link_32 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.453975304825623,0.92954341931271,0.128821183947774)
dA = chrono.ChVector3d(0.495143279359837,0.0150103475827935,0.868681657668809)
cB = chrono.ChVector3d(-0.463500826789943,0.928800926040933,0.134263503609747)
dB = chrono.ChVector3d(-0.495143279359834,-0.0150103475827762,-0.868681657668812)
link_32.SetFlipped(True)
link_32.Initialize(body_4,body_3,False,cA,cB,dA,dB)
link_32.SetName("Coincident18")
exported_items.append(link_32)


# Mate constraint: Coincident19 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_6 , SW name: Assem4^industrial robotic arm_2-1/head rot ND-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_4 , SW name: Assem3^industrial robotic arm_2-1/Mod base-1 ,  SW ref.type:2 (2)
link_33 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.523486535356467,0.878596297053088,0.161839899604579)
cB = chrono.ChVector3d(-0.52348653535647,0.878596297053088,0.161839899604571)
dA = chrono.ChVector3d(-0.0660877001742837,0.997604615459867,0.0204315221861854)
dB = chrono.ChVector3d(0.066087700174286,-0.997604615459867,-0.020431522186187)
link_33.Initialize(body_6,body_4,False,cA,cB,dB)
link_33.SetDistance(0)
link_33.SetName("Coincident19")
exported_items.append(link_33)

link_34 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.523486535356467,0.878596297053088,0.161839899604579)
dA = chrono.ChVector3d(-0.0660877001742837,0.997604615459867,0.0204315221861854)
cB = chrono.ChVector3d(-0.52348653535647,0.878596297053088,0.161839899604571)
dB = chrono.ChVector3d(0.066087700174286,-0.997604615459867,-0.020431522186187)
link_34.SetFlipped(True)
link_34.Initialize(body_6,body_4,False,cA,cB,dA,dB)
link_34.SetName("Coincident19")
exported_items.append(link_34)


# Mate constraint: Concentric7 [MateConcentric] type:1 align:0 flip:False
#   Entity 0: C::E name: body_6 , SW name: Assem4^industrial robotic arm_2-1/head rot ND-1 ,  SW ref.type:1 (1)
#   Entity 1: C::E name: body_4 , SW name: Assem3^industrial robotic arm_2-1/Mod base-1 ,  SW ref.type:1 (1)
link_35 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.523486535356467,0.878596297053088,0.161839899604579)
dA = chrono.ChVector3d(-0.0660877001742837,0.997604615459867,0.0204315221861854)
cB = chrono.ChVector3d(-0.52348653535647,0.878596297053088,0.161839899604571)
dB = chrono.ChVector3d(-0.066087700174286,0.997604615459867,0.020431522186187)
link_35.Initialize(body_6,body_4,False,cA,cB,dA,dB)
link_35.SetName("Concentric7")
exported_items.append(link_35)

link_36 = chrono.ChLinkMateGeneric()
link_36.SetConstrainedCoords(True, True, False, False, False, False)
cA = chrono.ChVector3d(-0.523486535356467,0.878596297053088,0.161839899604579)
cB = chrono.ChVector3d(-0.52348653535647,0.878596297053088,0.161839899604571)
dA = chrono.ChVector3d(-0.0660877001742837,0.997604615459867,0.0204315221861854)
dB = chrono.ChVector3d(-0.066087700174286,0.997604615459867,0.020431522186187)
link_36.Initialize(body_6,body_4,False,cA,cB,dA,dB)
link_36.SetName("Concentric7")
exported_items.append(link_36)


# Mate constraint: Coincident20 [MateCoincident] type:0 align:1 flip:False
#   Entity 0: C::E name: body_2 , SW name: Assem5^industrial robotic arm_2-1/A05-2-3-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_6 , SW name: Assem4^industrial robotic arm_2-1/heat rot-1 ,  SW ref.type:2 (2)
link_37 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.439078646561753,0.69593402152826,0.104343584198496)
cB = chrono.ChVector3d(-0.523623894749517,0.746912487812385,0.13048139970016)
dA = chrono.ChVector3d(0.295364527201867,5.84052821429789e-16,0.955384632528082)
dB = chrono.ChVector3d(-0.295364527201869,1.94635974004598e-15,-0.955384632528081)
link_37.Initialize(body_2,body_6,False,cA,cB,dB)
link_37.SetDistance(0)
link_37.SetName("Coincident20")
exported_items.append(link_37)

link_38 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.439078646561753,0.69593402152826,0.104343584198496)
dA = chrono.ChVector3d(0.295364527201867,5.84052821429789e-16,0.955384632528082)
cB = chrono.ChVector3d(-0.523623894749517,0.746912487812385,0.13048139970016)
dB = chrono.ChVector3d(-0.295364527201869,1.94635974004598e-15,-0.955384632528081)
link_38.SetFlipped(True)
link_38.Initialize(body_2,body_6,False,cA,cB,dA,dB)
link_38.SetName("Coincident20")
exported_items.append(link_38)


# Mate constraint: Concentric8 [MateConcentric] type:1 align:0 flip:False
#   Entity 0: C::E name: body_2 , SW name: Assem5^industrial robotic arm_2-1/A05-2-3-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_6 , SW name: Assem4^industrial robotic arm_2-1/heat rot-1 ,  SW ref.type:2 (2)
link_39 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.507223777120861,0.766864580121592,0.188213108095559)
dA = chrono.ChVector3d(-0.295364527201867,-5.87203896618149e-16,-0.955384632528082)
cB = chrono.ChVector3d(-0.507223777120891,0.766864580121582,0.188213108095569)
dB = chrono.ChVector3d(-0.295364527201869,1.94635974004598e-15,-0.955384632528081)
link_39.Initialize(body_2,body_6,False,cA,cB,dA,dB)
link_39.SetName("Concentric8")
exported_items.append(link_39)

link_40 = chrono.ChLinkMateGeneric()
link_40.SetConstrainedCoords(True, True, False, False, False, False)
cA = chrono.ChVector3d(-0.507223777120861,0.766864580121592,0.188213108095559)
cB = chrono.ChVector3d(-0.507223777120891,0.766864580121582,0.188213108095569)
dA = chrono.ChVector3d(-0.295364527201867,-5.87203896618149e-16,-0.955384632528082)
dB = chrono.ChVector3d(-0.295364527201869,1.94635974004598e-15,-0.955384632528081)
link_40.Initialize(body_2,body_6,False,cA,cB,dA,dB)
link_40.SetName("Concentric8")
exported_items.append(link_40)

