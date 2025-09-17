# PyChrono model automatically generated using Chrono::SolidWorks add-in
# Assembly: C:\Users\sbel\Documents\BCN3D-Moveo\CAD files\BCN3D Moveo assembly exp.SLDASM


import pychrono as chrono 
import builtins 

# Some global settings 
sphereswept_r = 0.001
chrono.ChCollisionModel.SetDefaultSuggestedEnvelope(0.006)
chrono.ChCollisionModel.SetDefaultSuggestedMargin(0.006)
chrono.ChCollisionSystemBullet.SetContactBreakingThreshold(0.004)

shapes_dir = 'moveo_arm_shapes/' 

if hasattr(builtins, 'exported_system_relpath'): 
    shapes_dir = builtins.exported_system_relpath + shapes_dir 

exported_items = [] 

body_0 = chrono.ChBodyAuxRef()
body_0.SetName('SLDW_GROUND')
body_0.SetFixed(True)
exported_items.append(body_0)

# Rigid body part
body_1 = chrono.ChBodyAuxRef()
body_1.SetName('finger-2')
body_1.SetPos(chrono.ChVector3d(0.152732010170369,-0.644860315070695,0.946677060407779))
body_1.SetRot(chrono.ChQuaterniond(-0.294111916042951,-0.490014969589048,0.54173539587051,0.616365371578588))
body_1.SetMass(0.187774871171945)
body_1.SetInertiaXX(chrono.ChVector3d(0.000265174127444158,0.000196242523084067,0.00029440481143436))
body_1.SetInertiaXY(chrono.ChVector3d(-3.78755493767497e-05,-1.32757797487314e-05,-6.24455478010594e-05))
body_1.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.0144947595028191,0.041295626856311,0.0448430881139618),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_1_1_shape = chrono.ChVisualShapeModelFile() 
body_1_1_shape.SetFilename(shapes_dir +'body_1_1.obj') 
body_1.AddVisualShape(body_1_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_1)



# Rigid body part
body_2 = chrono.ChBodyAuxRef()
body_2.SetName('base')
body_2.SetPos(chrono.ChVector3d(-0.00640548377770983,-0.566916227898278,-0.00245373776187163))
body_2.SetRot(chrono.ChQuaterniond(0.707106781186546,0.707106781186549,0,0))
body_2.SetMass(1.31250152456489)
body_2.SetInertiaXX(chrono.ChVector3d(0.0124801801428193,0.0124760560343789,0.0215814209629141))
body_2.SetInertiaXY(chrono.ChVector3d(2.06718269574179e-06,1.12408919829749e-06,4.64774744223533e-07))
body_2.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.00032373239178777,0.00621941987995098,0.32001076088812),chrono.ChQuaterniond(1,0,0,0)))
body_2.SetFixed(True)

# Visualization shape 
body_2_1_shape = chrono.ChVisualShapeModelFile() 
body_2_1_shape.SetFilename(shapes_dir +'body_2_1.obj') 
body_2.AddVisualShape(body_2_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.000349791739989946,-0.0691556729803845,0.32), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_2_2_shape = chrono.ChVisualShapeModelFile() 
body_2_2_shape.SetFilename(shapes_dir +'body_2_2.obj') 
body_2.AddVisualShape(body_2_2_shape, chrono.ChFramed(chrono.ChVector3d(-0.000349791739989946,0.00674432701961547,0.32), chrono.ChQuaterniond(0.995222668612713,0,-0.0976311419547525,0)))

# Visualization shape 
body_2_3_shape = chrono.ChVisualShapeModelFile() 
body_2_3_shape.SetFilename(shapes_dir +'body_2_3.obj') 
body_2.AddVisualShape(body_2_3_shape, chrono.ChFramed(chrono.ChVector3d(-0.000349791739989946,-0.00735567298038453,0.32), chrono.ChQuaterniond(0.694867873007362,0.130990988477166,-0.130990988477166,-0.694867873007362)))

# Visualization shape 
body_2_3_shape = chrono.ChVisualShapeModelFile() 
body_2_3_shape.SetFilename(shapes_dir +'body_2_3.obj') 
body_2.AddVisualShape(body_2_3_shape, chrono.ChFramed(chrono.ChVector3d(-0.000349791739989946,0.0608443270196155,0.32), chrono.ChQuaterniond(0.707106781186548,0,0,0.707106781186547)))

exported_items.append(body_2)



# Rigid body part
body_3 = chrono.ChBodyAuxRef()
body_3.SetName('endeffector')
body_3.SetPos(chrono.ChVector3d(0.158668902035524,-0.647571638573526,0.947250962863494))
body_3.SetRot(chrono.ChQuaterniond(-0.294111916042951,-0.490014969589048,0.541735395870509,0.616365371578588))
body_3.SetMass(0.76464695338024)
body_3.SetInertiaXX(chrono.ChVector3d(0.00448004325818126,0.0044986748387685,0.00160519712197591))
body_3.SetInertiaXY(chrono.ChVector3d(5.13076972458738e-09,1.24085986197339e-06,-1.25601029011369e-05))
body_3.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(3.89609093959617e-07,-0.0795425409655544,0.000145948351838478),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_3_1_shape = chrono.ChVisualShapeModelFile() 
body_3_1_shape.SetFilename(shapes_dir +'body_3_1.obj') 
body_3.AddVisualShape(body_3_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_3)



# Rigid body part
body_4 = chrono.ChBodyAuxRef()
body_4.SetName('shoulder')
body_4.SetPos(chrono.ChVector3d(-0.125182547329496,-1.35723524889837,0.0241031513745621))
body_4.SetRot(chrono.ChQuaterniond(0.0869806558174962,0.0869806558174965,0.70173667818745,0.701736678187452))
body_4.SetMass(8.48465549031483)
body_4.SetInertiaXX(chrono.ChVector3d(0.116753842200343,0.228417161676042,0.199585101395593))
body_4.SetInertiaXY(chrono.ChVector3d(0.0509041600779246,0.0223523317809518,-0.0128075568860269))
body_4.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-2.05620646996349e-06,0.181588005347366,0.484779860724548),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_4_1_shape = chrono.ChVisualShapeModelFile() 
body_4_1_shape.SetFilename(shapes_dir +'body_4_1.obj') 
body_4.AddVisualShape(body_4_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.134528973387898,0.365287437883171,0.433599850522472), chrono.ChQuaterniond(-0.303931148579979,0.704884549088414,-0.638455837879845,-0.0560158232682797)))

# Visualization shape 
body_4_2_shape = chrono.ChVisualShapeModelFile() 
body_4_2_shape.SetFilename(shapes_dir +'body_4_2.obj') 
body_4.AddVisualShape(body_4_2_shape, chrono.ChFramed(chrono.ChVector3d(-0.0826871454953483,0.114587437883179,0.402988008357064), chrono.ChQuaterniond(0.458819476127292,0.666368228627696,0.538037813100787,-0.236544676278259)))

# Visualization shape 
body_4_2_shape = chrono.ChVisualShapeModelFile() 
body_4_2_shape.SetFilename(shapes_dir +'body_4_2.obj') 
body_4.AddVisualShape(body_4_2_shape, chrono.ChFramed(chrono.ChVector3d(-0.116311409945233,0.20878743788318,0.490982603874077), chrono.ChQuaterniond(0.128330415526909,0.695364152405551,0.695364152405551,0.128330415526909)))

# Visualization shape 
body_4_4_shape = chrono.ChVisualShapeModelFile() 
body_4_4_shape.SetFilename(shapes_dir +'body_4_4.obj') 
body_4.AddVisualShape(body_4_4_shape, chrono.ChFramed(chrono.ChVector3d(0.206556370021406,0.125287437883179,0.392651242348821), chrono.ChQuaterniond(0.18148661410313,-4.27385016568213E-17,0.983393415120003,-8.9456331631041E-18)))

# Visualization shape 
body_4_2_shape = chrono.ChVisualShapeModelFile() 
body_4_2_shape.SetFilename(shapes_dir +'body_4_2.obj') 
body_4.AddVisualShape(body_4_2_shape, chrono.ChFramed(chrono.ChVector3d(-0.0826871454953482,0.208787437883179,0.402988008357064), chrono.ChQuaterniond(0.132897627255128,0.696192531829196,0.694505738399588,0.123757660875007)))

# Visualization shape 
body_4_6_shape = chrono.ChVisualShapeModelFile() 
body_4_6_shape.SetFilename(shapes_dir +'body_4_6.obj') 
body_4.AddVisualShape(body_4_6_shape, chrono.ChFramed(chrono.ChVector3d(-0.107161226201781,0.208787437883179,0.393636036716012), chrono.ChQuaterniond(0.128330415526909,0.695364152405551,0.695364152405551,0.128330415526909)))

# Visualization shape 
body_4_7_shape = chrono.ChVisualShapeModelFile() 
body_4_7_shape.SetFilename(shapes_dir +'body_4_7.obj') 
body_4.AddVisualShape(body_4_7_shape, chrono.ChFramed(chrono.ChVector3d(-0.0516720665687905,0.161687437883179,0.465260914818697), chrono.ChQuaterniond(-0.439712954082926,0.674236740886965,-0.553762149312922,-0.213084061436149)))

# Visualization shape 
body_4_2_shape = chrono.ChVisualShapeModelFile() 
body_4_2_shape.SetFilename(shapes_dir +'body_4_2.obj') 
body_4.AddVisualShape(body_4_2_shape, chrono.ChFramed(chrono.ChVector3d(0.0826572614467528,0.114587437883179,0.567011991642939), chrono.ChQuaterniond(0.536061364901492,0.239405781030397,-0.461127111608014,0.665345678583115)))

# Visualization shape 
body_4_6_shape = chrono.ChVisualShapeModelFile() 
body_4_6_shape.SetFilename(shapes_dir +'body_4_6.obj') 
body_4.AddVisualShape(body_4_6_shape, chrono.ChFramed(chrono.ChVector3d(-0.140785490651668,0.114587437883179,0.481630632233032), chrono.ChQuaterniond(0.128330415526909,0.695364152405551,0.695364152405551,0.128330415526909)))

# Visualization shape 
body_4_10_shape = chrono.ChVisualShapeModelFile() 
body_4_10_shape.SetFilename(shapes_dir +'body_4_10.obj') 
body_4.AddVisualShape(body_4_10_shape, chrono.ChFramed(chrono.ChVector3d(0.119938618816194,0.148450123157427,0.435267906396063), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010576)))

# Visualization shape 
body_4_11_shape = chrono.ChVisualShapeModelFile() 
body_4_11_shape.SetFilename(shapes_dir +'body_4_11.obj') 
body_4.AddVisualShape(body_4_11_shape, chrono.ChFramed(chrono.ChVector3d(0.0867868078977068,0.221964218580461,0.480002868395628), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010576)))

# Visualization shape 
body_4_12_shape = chrono.ChVisualShapeModelFile() 
body_4_12_shape.SetFilename(shapes_dir +'body_4_12.obj') 
body_4.AddVisualShape(body_4_12_shape, chrono.ChFramed(chrono.ChVector3d(0.065755614029801,0.161947437883179,0.467804278803731), chrono.ChQuaterniond(-0.29637899874638,-0.493913963383384,0.641996486830024,-0.506012842499988)))

# Visualization shape 
body_4_11_shape = chrono.ChVisualShapeModelFile() 
body_4_11_shape.SetFilename(shapes_dir +'body_4_11.obj') 
body_4.AddVisualShape(body_4_11_shape, chrono.ChFramed(chrono.ChVector3d(0.0961280600757344,0.221964218580461,0.483572323220457), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010576)))

# Visualization shape 
body_4_11_shape = chrono.ChVisualShapeModelFile() 
body_4_11_shape.SetFilename(shapes_dir +'body_4_11.obj') 
body_4.AddVisualShape(body_4_11_shape, chrono.ChFramed(chrono.ChVector3d(0.0774455557196791,0.221964218580461,0.476433413570799), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010576)))

# Visualization shape 
body_4_15_shape = chrono.ChVisualShapeModelFile() 
body_4_15_shape.SetFilename(shapes_dir +'body_4_15.obj') 
body_4.AddVisualShape(body_4_15_shape, chrono.ChFramed(chrono.ChVector3d(0.102480111556793,0.221964218580461,0.48599955250134), chrono.ChQuaterniond(0.573374586915906,-0.591217060861927,0.413813464110358,0.387894814280604)))

# Visualization shape 
body_4_16_shape = chrono.ChVisualShapeModelFile() 
body_4_16_shape.SetFilename(shapes_dir +'body_4_16.obj') 
body_4.AddVisualShape(body_4_16_shape, chrono.ChFramed(chrono.ChVector3d(0.0634336774526377,0.221964218580461,0.471079231333556), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010576)))

# Visualization shape 
body_4_17_shape = chrono.ChVisualShapeModelFile() 
body_4_17_shape.SetFilename(shapes_dir +'body_4_17.obj') 
body_4.AddVisualShape(body_4_17_shape, chrono.ChFramed(chrono.ChVector3d(0.0972490103370977,0.221964218580461,0.484000657799436), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010576)))

# Visualization shape 
body_2_3_shape = chrono.ChVisualShapeModelFile() 
body_2_3_shape.SetFilename(shapes_dir +'body_2_3.obj') 
body_4.AddVisualShape(body_2_3_shape, chrono.ChFramed(chrono.ChVector3d(0.112080084112034,0.365287437883179,0.527833457897947), chrono.ChQuaterniond(-0.124529582849427,-0.132021869756363,-0.674769168883048,0.71536646386748)))

# Visualization shape 
body_4_6_shape = chrono.ChVisualShapeModelFile() 
body_4_6_shape.SetFilename(shapes_dir +'body_4_6.obj') 
body_4.AddVisualShape(body_4_6_shape, chrono.ChFramed(chrono.ChVector3d(-0.140785490651668,0.208787437883179,0.481630632233032), chrono.ChQuaterniond(0.128330415526909,0.695364152405551,0.695364152405551,0.128330415526909)))

# Visualization shape 
body_4_2_shape = chrono.ChVisualShapeModelFile() 
body_4_2_shape.SetFilename(shapes_dir +'body_4_2.obj') 
body_4.AddVisualShape(body_4_2_shape, chrono.ChFramed(chrono.ChVector3d(-0.116311409945236,0.114587437883179,0.490982603874084), chrono.ChQuaterniond(-0.239405781030397,0.536061364901492,0.665345678583115,0.461127111608014)))

# Visualization shape 
body_4_2_shape = chrono.ChVisualShapeModelFile() 
body_4_2_shape.SetFilename(shapes_dir +'body_4_2.obj') 
body_4.AddVisualShape(body_4_2_shape, chrono.ChFramed(chrono.ChVector3d(0.116281525896641,0.114587437883179,0.479017396125918), chrono.ChQuaterniond(-0.236544676278259,-0.538037813100787,0.666368228627696,-0.458819476127292)))

# Visualization shape 
body_4_6_shape = chrono.ChVisualShapeModelFile() 
body_4_6_shape.SetFilename(shapes_dir +'body_4_6.obj') 
body_4.AddVisualShape(body_4_6_shape, chrono.ChFramed(chrono.ChVector3d(0.140755606603073,0.114587437883179,0.48836936776697), chrono.ChQuaterniond(0.50665503175463,0.279913883559409,-0.493255186285674,0.649344452344585)))

# Visualization shape 
body_4_7_shape = chrono.ChVisualShapeModelFile() 
body_4_7_shape.SetFilename(shapes_dir +'body_4_7.obj') 
body_4.AddVisualShape(body_4_7_shape, chrono.ChFramed(chrono.ChVector3d(0.0516421825201951,0.161687437883179,0.504739085181305), chrono.ChQuaterniond(0.704753912921666,0.197719373198742,-0.057636119071299,-0.678901354735647)))

# Visualization shape 
body_4_24_shape = chrono.ChVisualShapeModelFile() 
body_4_24_shape.SetFilename(shapes_dir +'body_4_24.obj') 
body_4.AddVisualShape(body_4_24_shape, chrono.ChFramed(chrono.ChVector3d(-0.130792472516685,0.365287437883179,0.435027632452397), chrono.ChQuaterniond(0.128330415526909,0.695364152405551,0.695364152405551,0.128330415526909)))

# Visualization shape 
body_4_6_shape = chrono.ChVisualShapeModelFile() 
body_4_6_shape.SetFilename(shapes_dir +'body_4_6.obj') 
body_4.AddVisualShape(body_4_6_shape, chrono.ChFramed(chrono.ChVector3d(0.140755606603073,0.208787437883179,0.48836936776697), chrono.ChQuaterniond(0.50665503175463,0.279913883559409,-0.493255186285674,0.649344452344585)))

# Visualization shape 
body_4_6_shape = chrono.ChVisualShapeModelFile() 
body_4_6_shape.SetFilename(shapes_dir +'body_4_6.obj') 
body_4.AddVisualShape(body_4_6_shape, chrono.ChFramed(chrono.ChVector3d(0.107131342153185,0.114587437883179,0.57636396328399), chrono.ChQuaterniond(0.50665503175463,0.279913883559409,-0.493255186285674,0.649344452344585)))

# Visualization shape 
body_4_27_shape = chrono.ChVisualShapeModelFile() 
body_4_27_shape.SetFilename(shapes_dir +'body_4_27.obj') 
body_4.AddVisualShape(body_4_27_shape, chrono.ChFramed(chrono.ChVector3d(-0.106972279462714,0.161687437883179,0.444129742255711), chrono.ChQuaterniond(0.823694567932461,-3.65422192679587E-17,0.567033736878642,2.3897286842733E-17)))

# Visualization shape 
body_4_6_shape = chrono.ChVisualShapeModelFile() 
body_4_6_shape.SetFilename(shapes_dir +'body_4_6.obj') 
body_4.AddVisualShape(body_4_6_shape, chrono.ChFramed(chrono.ChVector3d(-0.107161226201781,0.114587437883179,0.393636036716012), chrono.ChQuaterniond(0.128330415526909,0.695364152405551,0.695364152405551,0.128330415526909)))

# Visualization shape 
body_2_3_shape = chrono.ChVisualShapeModelFile() 
body_2_3_shape.SetFilename(shapes_dir +'body_2_3.obj') 
body_4.AddVisualShape(body_2_3_shape, chrono.ChFramed(chrono.ChVector3d(-0.125187721209868,0.365287437883179,0.437169305347294), chrono.ChQuaterniond(-0.124529582849427,-0.132021869756363,-0.674769168883048,0.71536646386748)))

# Visualization shape 
body_4_30_shape = chrono.ChVisualShapeModelFile() 
body_4_30_shape.SetFilename(shapes_dir +'body_4_30.obj') 
body_4.AddVisualShape(body_4_30_shape, chrono.ChFramed(chrono.ChVector3d(-0.0390841343186718,0.215289313036883,0.378519382193326), chrono.ChQuaterniond(0.128330415526909,-0.128330415526909,0.695364152405551,0.695364152405551)))

# Visualization shape 
body_4_2_shape = chrono.ChVisualShapeModelFile() 
body_4_2_shape.SetFilename(shapes_dir +'body_4_2.obj') 
body_4.AddVisualShape(body_4_2_shape, chrono.ChFramed(chrono.ChVector3d(0.0826572614467527,0.208787437883179,0.567011991642938), chrono.ChQuaterniond(0.538037813100802,0.236544676278237,-0.458819476127274,0.666368228627704)))

# Visualization shape 
body_4_6_shape = chrono.ChVisualShapeModelFile() 
body_4_6_shape.SetFilename(shapes_dir +'body_4_6.obj') 
body_4.AddVisualShape(body_4_6_shape, chrono.ChFramed(chrono.ChVector3d(0.107131342153185,0.208787437883179,0.57636396328399), chrono.ChQuaterniond(0.50665503175463,0.279913883559409,-0.493255186285674,0.649344452344585)))

# Visualization shape 
body_4_2_shape = chrono.ChVisualShapeModelFile() 
body_4_2_shape.SetFilename(shapes_dir +'body_4_2.obj') 
body_4.AddVisualShape(body_4_2_shape, chrono.ChFramed(chrono.ChVector3d(0.116281525896641,0.208787437883179,0.479017396125918), chrono.ChQuaterniond(0.541041588051587,0.232160147894178,-0.455273544145294,0.667908426155677)))

# Visualization shape 
body_4_27_shape = chrono.ChVisualShapeModelFile() 
body_4_27_shape.SetFilename(shapes_dir +'body_4_27.obj') 
body_4.AddVisualShape(body_4_27_shape, chrono.ChFramed(chrono.ChVector3d(0.106942395414119,0.161687437883179,0.525870257744292), chrono.ChQuaterniond(0.567033736878642,-4.46890637505636E-17,-0.82369456793246,8.3757262549602E-17)))

# Visualization shape 
body_4_35_shape = chrono.ChVisualShapeModelFile() 
body_4_35_shape.SetFilename(shapes_dir +'body_4_35.obj') 
body_4.AddVisualShape(body_4_35_shape, chrono.ChFramed(chrono.ChVector3d(-0.0151358876780854,0.148450123157427,0.383653589629038), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010575)))

# Visualization shape 
body_4_11_shape = chrono.ChVisualShapeModelFile() 
body_4_11_shape.SetFilename(shapes_dir +'body_4_11.obj') 
body_4.AddVisualShape(body_4_11_shape, chrono.ChFramed(chrono.ChVector3d(-0.0613654516458117,0.221964218580461,0.423391314873842), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010575)))

# Visualization shape 
body_4_12_shape = chrono.ChVisualShapeModelFile() 
body_4_12_shape.SetFilename(shapes_dir +'body_4_12.obj') 
body_4.AddVisualShape(body_4_12_shape, chrono.ChFramed(chrono.ChVector3d(-0.0336353091444132,0.161947437883179,0.429825279467552), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010575)))

# Visualization shape 
body_4_15_shape = chrono.ChVisualShapeModelFile() 
body_4_15_shape.SetFilename(shapes_dir +'body_4_15.obj') 
body_4.AddVisualShape(body_4_15_shape, chrono.ChFramed(chrono.ChVector3d(-0.0716408290416421,0.221964218580461,0.419464914566531), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010575)))

# Visualization shape 
body_4_16_shape = chrono.ChVisualShapeModelFile() 
body_4_16_shape.SetFilename(shapes_dir +'body_4_16.obj') 
body_4.AddVisualShape(body_4_16_shape, chrono.ChFramed(chrono.ChVector3d(-0.0380123212007426,0.221964218580461,0.432314951935915), chrono.ChQuaterniond(0.406097279914884,0.685687234667515,0.578865268646973,-0.172722367439822)))

# Visualization shape 
body_4_11_shape = chrono.ChVisualShapeModelFile() 
body_4_11_shape.SetFilename(shapes_dir +'body_4_11.obj') 
body_4.AddVisualShape(body_4_11_shape, chrono.ChFramed(chrono.ChVector3d(-0.0520241994677841,0.221964218580461,0.426960769698671), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010575)))

# Visualization shape 
body_4_11_shape = chrono.ChVisualShapeModelFile() 
body_4_11_shape.SetFilename(shapes_dir +'body_4_11.obj') 
body_4.AddVisualShape(body_4_11_shape, chrono.ChFramed(chrono.ChVector3d(-0.0426829472897564,0.221964218580461,0.4305302245235), chrono.ChQuaterniond(-0.361191810986166,-0.438927448476822,0.607898409009708,-0.554384970010575)))

# Visualization shape 
body_4_30_shape = chrono.ChVisualShapeModelFile() 
body_4_30_shape.SetFilename(shapes_dir +'body_4_30.obj') 
body_4.AddVisualShape(body_4_30_shape, chrono.ChFramed(chrono.ChVector3d(0.10010052313394,0.215289313036884,0.431704259083276), chrono.ChQuaterniond(0.128330415526909,-0.128330415526909,0.695364152405551,0.695364152405551)))

# Visualization shape 
body_4_43_shape = chrono.ChVisualShapeModelFile() 
body_4_43_shape.SetFilename(shapes_dir +'body_4_43.obj') 
body_4.AddVisualShape(body_4_43_shape, chrono.ChFramed(chrono.ChVector3d(-1.49420242974707E-05,0.077287437883179,0.485000000000001), chrono.ChQuaterniond(-2.21949755945168E-17,-0.18148661410313,5.31371181545422E-19,0.983393415120003)))

# Visualization shape 
body_4_1_shape = chrono.ChVisualShapeModelFile() 
body_4_1_shape.SetFilename(shapes_dir +'body_4_1.obj') 
body_4.AddVisualShape(body_4_1_shape, chrono.ChFramed(chrono.ChVector3d(0.134499089339303,0.36528743788319,0.536400149477528), chrono.ChQuaterniond(0.582440014611571,0.582440014611561,0.40095340050843,-0.400953400508443)))

exported_items.append(body_4)



# Rigid body part
body_5 = chrono.ChBodyAuxRef()
body_5.SetName('bicep')
body_5.SetPos(chrono.ChVector3d(0.0414897445515171,-1.11959414546391,0.948133210877378))
body_5.SetRot(chrono.ChQuaterniond(-0.227802931432022,0.324280704911258,0.908807217938983,-0.130450333365774))
body_5.SetMass(3.86323930180119)
body_5.SetInertiaXX(chrono.ChVector3d(0.13373795092169,0.0436722542111458,0.118529299259012))
body_5.SetInertiaXY(chrono.ChVector3d(-0.00964379404000941,-0.0069559729697411,-0.0346720923736778))
body_5.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(0.0354670150898731,0.48317483901602,0.382897524002177),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_5_1_shape = chrono.ChVisualShapeModelFile() 
body_5_1_shape.SetFilename(shapes_dir +'body_5_1.obj') 
body_5.AddVisualShape(body_5_1_shape, chrono.ChFramed(chrono.ChVector3d(0.21237577925116,0.666333036970263,0.270963058597319), chrono.ChQuaterniond(-0.13235354525281,-0.601609327823853,0.694609657240491,-0.371572576763398)))

# Visualization shape 
body_5_1_shape = chrono.ChVisualShapeModelFile() 
body_5_1_shape.SetFilename(shapes_dir +'body_5_1.obj') 
body_5.AddVisualShape(body_5_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.0110051399383631,0.723829342533664,0.17197242446489), chrono.ChQuaterniond(0.371572570145313,0.694609627158172,0.601609362556473,-0.132353563832582)))

# Visualization shape 
body_2_3_shape = chrono.ChVisualShapeModelFile() 
body_2_3_shape.SetFilename(shapes_dir +'body_2_3.obj') 
body_5.AddVisualShape(body_2_3_shape, chrono.ChFramed(chrono.ChVector3d(0.200022330784888,0.691404965644667,0.241657906335273), chrono.ChQuaterniond(0.16915338155244,0.0657611177520045,0.916565237530002,-0.35632958655289)))

# Visualization shape 
body_5_4_shape = chrono.ChVisualShapeModelFile() 
body_5_4_shape.SetFilename(shapes_dir +'body_5_4.obj') 
body_5.AddVisualShape(body_5_4_shape, chrono.ChFramed(chrono.ChVector3d(0.169449484810039,0.539822471770495,0.327830355391498), chrono.ChQuaterniond(-0.132353563832582,-0.601609362556473,0.694609627158172,-0.371572570145313)))

# Visualization shape 
body_5_5_shape = chrono.ChVisualShapeModelFile() 
body_5_5_shape.SetFilename(shapes_dir +'body_5_5.obj') 
body_5.AddVisualShape(body_5_5_shape, chrono.ChFramed(chrono.ChVector3d(0.0696057418354057,0.524113493978709,0.384608096382784), chrono.ChQuaterniond(0.00327115834129586,-0.661686833194137,0.707099214766292,-0.249340198879993)))

# Visualization shape 
body_5_5_shape = chrono.ChVisualShapeModelFile() 
body_5_5_shape.SetFilename(shapes_dir +'body_5_5.obj') 
body_5.AddVisualShape(body_5_5_shape, chrono.ChFramed(chrono.ChVector3d(0.0895765118035918,0.526567242524567,0.3323446534714), chrono.ChQuaterniond(-0.399541035396055,0.687592147163971,-0.583409771116879,-0.164975874473937)))

# Visualization shape 
body_5_1_shape = chrono.ChVisualShapeModelFile() 
body_5_1_shape.SetFilename(shapes_dir +'body_5_1.obj') 
body_5.AddVisualShape(body_5_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.0155507797810393,0.666333045967212,0.18386834979936), chrono.ChQuaterniond(0.371572570145313,0.694609627158172,0.601609362556473,-0.132353563832582)))

# Visualization shape 
body_4_16_shape = chrono.ChVisualShapeModelFile() 
body_4_16_shape.SetFilename(shapes_dir +'body_4_16.obj') 
body_5.AddVisualShape(body_4_16_shape, chrono.ChFramed(chrono.ChVector3d(0.09968782827052,0.55714664028102,0.330256839691665), chrono.ChQuaterniond(0.623201317685924,0.0896385763669729,-0.334095970694842,0.701402114073591)))

# Visualization shape 
body_4_11_shape = chrono.ChVisualShapeModelFile() 
body_4_11_shape.SetFilename(shapes_dir +'body_4_11.obj') 
body_5.AddVisualShape(body_4_11_shape, chrono.ChFramed(chrono.ChVector3d(0.110990743405934,0.55714664028102,0.334575880029708), chrono.ChQuaterniond(0.623201317685924,0.0896385763669729,-0.334095970694842,0.701402114073591)))

# Visualization shape 
body_4_11_shape = chrono.ChVisualShapeModelFile() 
body_4_11_shape.SetFilename(shapes_dir +'body_4_11.obj') 
body_5.AddVisualShape(body_4_11_shape, chrono.ChFramed(chrono.ChVector3d(0.120331995583961,0.55714664028102,0.338145334854537), chrono.ChQuaterniond(0.623201317685924,0.0896385763669729,-0.334095970694842,0.701402114073591)))

# Visualization shape 
body_4_15_shape = chrono.ChVisualShapeModelFile() 
body_4_15_shape.SetFilename(shapes_dir +'body_4_15.obj') 
body_5.AddVisualShape(body_4_15_shape, chrono.ChFramed(chrono.ChVector3d(0.132195385850056,0.55714664028102,0.342678542482069), chrono.ChQuaterniond(0.700702587337082,0.16141555660316,-0.0949520094527719,-0.688436647838051)))

# Visualization shape 
body_5_12_shape = chrono.ChVisualShapeModelFile() 
body_5_12_shape.SetFilename(shapes_dir +'body_5_12.obj') 
body_5.AddVisualShape(body_5_12_shape, chrono.ChFramed(chrono.ChVector3d(0.0937094268765823,0.55714664028102,0.327972388603774), chrono.ChQuaterniond(0.936636068980125,0.299625571650419,-0.17285748124043,0.0552963134199077)))

# Visualization shape 
body_4_11_shape = chrono.ChVisualShapeModelFile() 
body_4_11_shape.SetFilename(shapes_dir +'body_4_11.obj') 
body_5.AddVisualShape(body_4_11_shape, chrono.ChFramed(chrono.ChVector3d(0.129673247761989,0.55714664028102,0.341714789679366), chrono.ChQuaterniond(0.623201317685924,0.0896385763669729,-0.334095970694842,0.701402114073591)))

# Visualization shape 
body_5_14_shape = chrono.ChVisualShapeModelFile() 
body_5_14_shape.SetFilename(shapes_dir +'body_5_14.obj') 
body_5.AddVisualShape(body_5_14_shape, chrono.ChFramed(chrono.ChVector3d(0.184290524404932,0.416928428874706,0.366874442906095), chrono.ChQuaterniond(0.16915338155244,0.0657611177520045,0.916565237530002,-0.35632958655289)))

# Visualization shape 
body_5_15_shape = chrono.ChVisualShapeModelFile() 
body_5_15_shape.SetFilename(shapes_dir +'body_5_15.obj') 
body_5.AddVisualShape(body_5_15_shape, chrono.ChFramed(chrono.ChVector3d(0.0913972045377182,0.462086744609975,0.372427688667124), chrono.ChQuaterniond(0.41135650645918,-0.033327048004969,0.836355502004232,-0.360811040202793)))

# Visualization shape 
body_5_16_shape = chrono.ChVisualShapeModelFile() 
body_5_16_shape.SetFilename(shapes_dir +'body_5_16.obj') 
body_5.AddVisualShape(body_5_16_shape, chrono.ChFramed(chrono.ChVector3d(0.0171915622702742,0.525340368251638,0.334632416697235), chrono.ChQuaterniond(-0.331813957388773,0.518990162389224,-0.228421693588338,0.753904661693668)))

# Visualization shape 
body_5_15_shape = chrono.ChVisualShapeModelFile() 
body_5_15_shape.SetFilename(shapes_dir +'body_5_15.obj') 
body_5.AddVisualShape(body_5_15_shape, chrono.ChFramed(chrono.ChVector3d(-0.0121312949710655,0.511018522773644,0.390055517060794), chrono.ChQuaterniond(0.65000350823401,-0.328747650340362,-0.667982140796094,0.152382024060051)))

# Visualization shape 
body_5_15_shape = chrono.ChVisualShapeModelFile() 
body_5_15_shape.SetFilename(shapes_dir +'body_5_15.obj') 
body_5.AddVisualShape(body_5_15_shape, chrono.ChFramed(chrono.ChVector3d(0.0723289522571371,0.511018522773644,0.422329245596255), chrono.ChQuaterniond(0.16915338155244,0.0657611177520045,0.916565237530002,-0.35632958655289)))

# Visualization shape 
body_5_5_shape = chrono.ChVisualShapeModelFile() 
body_5_5_shape.SetFilename(shapes_dir +'body_5_5.obj') 
body_5.AddVisualShape(body_5_5_shape, chrono.ChFramed(chrono.ChVector3d(0.0800290540487953,0.497365830194354,0.357330320729676), chrono.ChQuaterniond(-0.361120181032636,-0.438992767495321,0.607940963294099,-0.554333248224206)))

# Visualization shape 
body_5_1_shape = chrono.ChVisualShapeModelFile() 
body_5_1_shape.SetFilename(shapes_dir +'body_5_1.obj') 
body_5.AddVisualShape(body_5_1_shape, chrono.ChFramed(chrono.ChVector3d(0.232422080813958,0.684052499436178,0.218501964026462), chrono.ChQuaterniond(-0.13235354525281,-0.601609327823853,0.694609657240491,-0.371572576763398)))

# Visualization shape 
body_5_15_shape = chrono.ChVisualShapeModelFile() 
body_5_15_shape.SetFilename(shapes_dir +'body_5_15.obj') 
body_5.AddVisualShape(body_5_15_shape, chrono.ChFramed(chrono.ChVector3d(0.00693695730951549,0.462086744609975,0.340153960131663), chrono.ChQuaterniond(-0.152870343622119,0.183102385002807,0.919421208793831,-0.312680052877107)))

# Visualization shape 
body_4_7_shape = chrono.ChVisualShapeModelFile() 
body_4_7_shape.SetFilename(shapes_dir +'body_4_7.obj') 
body_5.AddVisualShape(body_4_7_shape, chrono.ChFramed(chrono.ChVector3d(0.120879461446381,0.525340368251638,0.374253365252836), chrono.ChQuaterniond(0.118999371027366,-0.693581767838107,0.697021627853176,-0.137638407875727)))

# Visualization shape 
body_4_12_shape = chrono.ChVisualShapeModelFile() 
body_4_12_shape.SetFilename(shapes_dir +'body_4_12.obj') 
body_5.AddVisualShape(body_4_12_shape, chrono.ChFramed(chrono.ChVector3d(0.101258343910438,0.539822471770495,0.301773335170248), chrono.ChQuaterniond(-0.132353563832582,-0.601609362556473,0.694609627158172,-0.371572570145313)))

# Visualization shape 
body_5_5_shape = chrono.ChVisualShapeModelFile() 
body_5_5_shape.SetFilename(shapes_dir +'body_5_5.obj') 
body_5.AddVisualShape(body_5_5_shape, chrono.ChFramed(chrono.ChVector3d(0.0791531995902023,0.553314906308922,0.359622429124509), chrono.ChQuaterniond(-0.132353563832582,-0.601609362556473,0.694609627158172,-0.371572570145313)))

# Visualization shape 
body_5_1_shape = chrono.ChVisualShapeModelFile() 
body_5_1_shape.SetFilename(shapes_dir +'body_5_1.obj') 
body_5.AddVisualShape(body_5_1_shape, chrono.ChFramed(chrono.ChVector3d(0.216921423858168,0.723829333536715,0.259067135083383), chrono.ChQuaterniond(-0.13235354525281,-0.601609327823853,0.694609657240491,-0.371572576763398)))

# Visualization shape 
body_5_1_shape = chrono.ChVisualShapeModelFile() 
body_5_1_shape.SetFilename(shapes_dir +'body_5_1.obj') 
body_5.AddVisualShape(body_5_1_shape, chrono.ChFramed(chrono.ChVector3d(0.00449551701742712,0.684052508433127,0.131407253407969), chrono.ChQuaterniond(0.371572570145313,0.694609627158172,0.601609362556473,-0.132353563832582)))

# Visualization shape 
body_5_27_shape = chrono.ChVisualShapeModelFile() 
body_5_27_shape.SetFilename(shapes_dir +'body_5_27.obj') 
body_5.AddVisualShape(body_5_27_shape, chrono.ChFramed(chrono.ChVector3d(0.219638960358746,0.691404965644667,0.249153761467414), chrono.ChQuaterniond(-0.132353563832582,-0.601609362556473,0.694609627158172,-0.371572570145313)))

# Visualization shape 
body_2_3_shape = chrono.ChVisualShapeModelFile() 
body_2_3_shape.SetFilename(shapes_dir +'body_2_3.obj') 
body_5.AddVisualShape(body_2_3_shape, chrono.ChFramed(chrono.ChVector3d(0.0012965319495285,0.691404965644667,0.165721324391864), chrono.ChQuaterniond(0.171681138704418,0.0588470705453789,0.930262003820792,-0.318865509500018)))

# Visualization shape 
body_5_29_shape = chrono.ChVisualShapeModelFile() 
body_5_29_shape.SetFilename(shapes_dir +'body_5_29.obj') 
body_5.AddVisualShape(body_5_29_shape, chrono.ChFramed(chrono.ChVector3d(0.0129690131334684,0.443678294600717,0.507051995183013), chrono.ChQuaterniond(-0.47580944052331,0.318777661324254,0.523073012407345,0.631174146048964)))

# Visualization shape 
body_5_30_shape = chrono.ChVisualShapeModelFile() 
body_5_30_shape.SetFilename(shapes_dir +'body_5_30.obj') 
body_5.AddVisualShape(body_5_30_shape, chrono.ChFramed(chrono.ChVector3d(-0.00536967242867104,0.283398221689367,0.442982347359002), chrono.ChQuaterniond(0.705182381142775,-0.203013276913292,-0.0521326128810577,0.677337146033588)))

# Visualization shape 
body_5_31_shape = chrono.ChVisualShapeModelFile() 
body_5_31_shape.SetFilename(shapes_dir +'body_5_31.obj') 
body_5.AddVisualShape(body_5_31_shape, chrono.ChFramed(chrono.ChVector3d(-1.49420242973597E-05,0.365287437883179,0.485), chrono.ChQuaterniond(0.584751280141228,0.162660575836334,-0.397575075140778,0.688143543941663)))

# Visualization shape 
body_5_30_shape = chrono.ChVisualShapeModelFile() 
body_5_30_shape.SetFilename(shapes_dir +'body_5_30.obj') 
body_5.AddVisualShape(body_5_30_shape, chrono.ChFramed(chrono.ChVector3d(-0.0243959955786422,0.443678294600717,0.492774175883698), chrono.ChQuaterniond(0.705197001068164,-0.203203581102361,-0.0519344749128066,0.677280078421901)))

# Visualization shape 
body_5_30_shape = chrono.ChVisualShapeModelFile() 
body_5_30_shape.SetFilename(shapes_dir +'body_5_30.obj') 
body_5.AddVisualShape(body_5_30_shape, chrono.ChFramed(chrono.ChVector3d(0.00967526388926926,0.356246720615382,0.403609795794356), chrono.ChQuaterniond(0.703885575312508,-0.188272544878961,-0.0674173335795779,0.681581579009292)))

# Visualization shape 
body_5_34_shape = chrono.ChVisualShapeModelFile() 
body_5_34_shape.SetFilename(shapes_dir +'body_5_34.obj') 
body_5.AddVisualShape(body_5_34_shape, chrono.ChFramed(chrono.ChVector3d(-1.49420242972487E-05,0.365287437883179,0.485), chrono.ChQuaterniond(0.688143543941663,0.397575075140778,0.162660575836334,-0.584751280141228)))

# Visualization shape 
body_5_30_shape = chrono.ChVisualShapeModelFile() 
body_5_30_shape.SetFilename(shapes_dir +'body_5_30.obj') 
body_5.AddVisualShape(body_5_30_shape, chrono.ChFramed(chrono.ChVector3d(-0.048981988253558,0.395313468653061,0.557115642268425), chrono.ChQuaterniond(0.704226090740745,-0.191808479610464,-0.0637621605657185,0.680594965562868)))

# Visualization shape 
body_5_29_shape = chrono.ChVisualShapeModelFile() 
body_5_29_shape.SetFilename(shapes_dir +'body_5_29.obj') 
body_5.AddVisualShape(body_5_29_shape, chrono.ChFramed(chrono.ChVector3d(-0.0116169795414478,0.395313468653061,0.571393461567741), chrono.ChQuaterniond(0.641506735678437,-0.0488610036259791,-0.297437570053274,-0.705416616138762)))

# Visualization shape 
body_4_15_shape = chrono.ChVisualShapeModelFile() 
body_4_15_shape.SetFilename(shapes_dir +'body_4_15.obj') 
body_5.AddVisualShape(body_4_15_shape, chrono.ChFramed(chrono.ChVector3d(-0.0203620837323916,0.485902610865597,0.410809687320732), chrono.ChQuaterniond(0.916565237530002,-0.35632958655289,-0.169153381552439,-0.0657611177520045)))

# Visualization shape 
body_4_15_shape = chrono.ChVisualShapeModelFile() 
body_4_15_shape.SetFilename(shapes_dir +'body_4_15.obj') 
body_5.AddVisualShape(body_4_15_shape, chrono.ChFramed(chrono.ChVector3d(-0.00115674115508968,0.437311021657353,0.361358102836117), chrono.ChQuaterniond(0.604773744325455,-0.121213994721949,0.70919208915048,-0.341471032950811)))

# Visualization shape 
body_4_15_shape = chrono.ChVisualShapeModelFile() 
body_4_15_shape.SetFilename(shapes_dir +'body_4_15.obj') 
body_5.AddVisualShape(body_4_15_shape, chrono.ChFramed(chrono.ChVector3d(0.0832881785342803,0.437311021657353,0.39362597445257), chrono.ChQuaterniond(0.604773744325455,-0.121213994721949,0.70919208915048,-0.341471032950811)))

# Visualization shape 
body_4_15_shape = chrono.ChVisualShapeModelFile() 
body_4_15_shape.SetFilename(shapes_dir +'body_4_15.obj') 
body_5.AddVisualShape(body_4_15_shape, chrono.ChFramed(chrono.ChVector3d(0.0642208872025141,0.486240333893177,0.44352501658164), chrono.ChQuaterniond(0.916565237530002,-0.35632958655289,-0.169153381552439,-0.0657611177520045)))

# Visualization shape 
body_5_29_shape = chrono.ChVisualShapeModelFile() 
body_5_29_shape.SetFilename(shapes_dir +'body_5_29.obj') 
body_5.AddVisualShape(body_5_29_shape, chrono.ChFramed(chrono.ChVector3d(0.0319953362834395,0.283398221689367,0.457260166658317), chrono.ChQuaterniond(0.641506735678437,-0.0488610036259791,-0.297437570053274,-0.705416616138762)))

# Visualization shape 
body_5_29_shape = chrono.ChVisualShapeModelFile() 
body_5_29_shape.SetFilename(shapes_dir +'body_5_29.obj') 
body_5.AddVisualShape(body_5_29_shape, chrono.ChFramed(chrono.ChVector3d(0.04704027260138,0.356246720615382,0.417887615093672), chrono.ChQuaterniond(0.641506735678437,-0.0488610036259791,-0.297437570053274,-0.705416616138762)))

# Visualization shape 
body_5_43_shape = chrono.ChVisualShapeModelFile() 
body_5_43_shape.SetFilename(shapes_dir +'body_5_43.obj') 
body_5.AddVisualShape(body_5_43_shape, chrono.ChFramed(chrono.ChVector3d(-0.00735346756733213,0.691404965644663,0.162416009224091), chrono.ChQuaterniond(0.0519344749128137,-0.677280078421902,0.705197001068163,-0.203203581102356)))

# Visualization shape 
body_5_43_shape = chrono.ChVisualShapeModelFile() 
body_5_43_shape.SetFilename(shapes_dir +'body_5_43.obj') 
body_5.AddVisualShape(body_5_43_shape, chrono.ChFramed(chrono.ChVector3d(0.220573094641097,0.69140495664772,0.249510719235717), chrono.ChQuaterniond(0.203203596484405,0.705197025316654,0.677280046585652,0.0519345006453649)))

exported_items.append(body_5)



# Rigid body part
body_6 = chrono.ChBodyAuxRef()
body_6.SetName('elbow')
body_6.SetPos(chrono.ChVector3d(0.0175665501533068,-0.769108283926751,0.342166797401707))
body_6.SetRot(chrono.ChQuaterniond(-0.371022147832538,0.527413038047445,0.274294542287069,0.713400698897066))
body_6.SetMass(2.2762403843209)
body_6.SetInertiaXX(chrono.ChVector3d(0.0182543021158534,0.0105401881576709,0.0150690850873653))
body_6.SetInertiaXY(chrono.ChVector3d(0.00174608193884081,0.00108586681615373,-0.00566425158223554))
body_6.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(0.201192849535152,0.0461442486033048,0.350097513593972),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_4_12_shape = chrono.ChVisualShapeModelFile() 
body_4_12_shape.SetFilename(shapes_dir +'body_4_12.obj') 
body_6.AddVisualShape(body_4_12_shape, chrono.ChFramed(chrono.ChVector3d(0.053130161580885,0.0757340438210331,0.396032651455244), chrono.ChQuaterniond(0.965925826289068,-3.20996601666863E-17,-0.25881904510252,5.2460759988303E-17)))

# Visualization shape 
body_5_4_shape = chrono.ChVisualShapeModelFile() 
body_5_4_shape.SetFilename(shapes_dir +'body_5_4.obj') 
body_6.AddVisualShape(body_5_4_shape, chrono.ChFramed(chrono.ChVector3d(0.319765316258015,0.00353404382103323,0.39), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_5_4_shape = chrono.ChVisualShapeModelFile() 
body_5_4_shape.SetFilename(shapes_dir +'body_5_4.obj') 
body_6.AddVisualShape(body_5_4_shape, chrono.ChFramed(chrono.ChVector3d(0.319765316258015,0.0105340438210332,0.31), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_4_12_shape = chrono.ChVisualShapeModelFile() 
body_4_12_shape.SetFilename(shapes_dir +'body_4_12.obj') 
body_6.AddVisualShape(body_4_12_shape, chrono.ChFramed(chrono.ChVector3d(0.319765316258015,0.0757340438210333,0.39), chrono.ChQuaterniond(0.965925826289068,6.76708490926232E-17,0.25881904510252,1.68895710623617E-17)))

# Visualization shape 
body_4_12_shape = chrono.ChVisualShapeModelFile() 
body_4_12_shape.SetFilename(shapes_dir +'body_4_12.obj') 
body_6.AddVisualShape(body_4_12_shape, chrono.ChFramed(chrono.ChVector3d(0.145195464491374,0.0757340438210332,0.303967348544756), chrono.ChQuaterniond(0.965925826289068,-3.56914959552404E-17,-0.258819045102521,6.58656736436308E-17)))

# Visualization shape 
body_5_4_shape = chrono.ChVisualShapeModelFile() 
body_5_4_shape.SetFilename(shapes_dir +'body_5_4.obj') 
body_6.AddVisualShape(body_5_4_shape, chrono.ChFramed(chrono.ChVector3d(0.145195464491374,0.0105340438210331,0.303967348544756), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_5_4_shape = chrono.ChVisualShapeModelFile() 
body_5_4_shape.SetFilename(shapes_dir +'body_5_4.obj') 
body_6.AddVisualShape(body_5_4_shape, chrono.ChFramed(chrono.ChVector3d(0.053130161580885,0.0105340438210331,0.303967348544756), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_4_12_shape = chrono.ChVisualShapeModelFile() 
body_4_12_shape.SetFilename(shapes_dir +'body_4_12.obj') 
body_6.AddVisualShape(body_4_12_shape, chrono.ChFramed(chrono.ChVector3d(0.145195464491373,0.0757340438210332,0.396032651455244), chrono.ChQuaterniond(0.707106781186547,-5.7547943534535E-17,-0.707106781186548,-5.66192584630602E-17)))

# Visualization shape 
body_4_12_shape = chrono.ChVisualShapeModelFile() 
body_4_12_shape.SetFilename(shapes_dir +'body_4_12.obj') 
body_6.AddVisualShape(body_4_12_shape, chrono.ChFramed(chrono.ChVector3d(0.319765316258015,0.0757340438210332,0.31), chrono.ChQuaterniond(0.965925826289068,-3.56914959552404E-17,-0.258819045102521,6.58656736436306E-17)))

# Visualization shape 
body_4_12_shape = chrono.ChVisualShapeModelFile() 
body_4_12_shape.SetFilename(shapes_dir +'body_4_12.obj') 
body_6.AddVisualShape(body_4_12_shape, chrono.ChFramed(chrono.ChVector3d(0.053130161580885,0.0757340438210332,0.303967348544756), chrono.ChQuaterniond(0.965925826289068,-3.38955780609633E-17,-0.25881904510252,5.91632168159667E-17)))

# Visualization shape 
body_6_11_shape = chrono.ChVisualShapeModelFile() 
body_6_11_shape.SetFilename(shapes_dir +'body_6_11.obj') 
body_6.AddVisualShape(body_6_11_shape, chrono.ChFramed(chrono.ChVector3d(0.354162813036129,0.0457340438210333,0.28), chrono.ChQuaterniond(2.77555756156289E-17,-2.94977448836907E-17,1,3.25871849309974E-17)))

# Visualization shape 
body_6_12_shape = chrono.ChVisualShapeModelFile() 
body_6_12_shape.SetFilename(shapes_dir +'body_6_12.obj') 
body_6.AddVisualShape(body_6_12_shape, chrono.ChFramed(chrono.ChVector3d(0.354162813036129,0.0457340438210332,0.42), chrono.ChQuaterniond(-7.84217251355006E-17,8.32667268468867E-17,-2.51526289044011E-17,1)))

# Visualization shape 
body_2_3_shape = chrono.ChVisualShapeModelFile() 
body_2_3_shape.SetFilename(shapes_dir +'body_2_3.obj') 
body_6.AddVisualShape(body_2_3_shape, chrono.ChFramed(chrono.ChVector3d(0.340162813036129,0.0457340438210331,0.35), chrono.ChQuaterniond(-7.84217251355006E-17,8.32667268468867E-17,-2.51526289044011E-17,1)))

# Visualization shape 
body_6_14_shape = chrono.ChVisualShapeModelFile() 
body_6_14_shape.SetFilename(shapes_dir +'body_6_14.obj') 
body_6.AddVisualShape(body_6_14_shape, chrono.ChFramed(chrono.ChVector3d(0.391362813036129,0.0457340438210333,0.35), chrono.ChQuaterniond(0.707106781186548,7.66640616636123E-17,4.10928727376708E-17,0.707106781186547)))

# Visualization shape 
body_6_15_shape = chrono.ChVisualShapeModelFile() 
body_6_15_shape.SetFilename(shapes_dir +'body_6_15.obj') 
body_6.AddVisualShape(body_6_15_shape, chrono.ChFramed(chrono.ChVector3d(0.200362813036129,0.0457340438210331,0.35), chrono.ChQuaterniond(0.707106781186547,-1.67061623184269E-17,1.79555395017045E-16,-0.707106781186548)))

# Visualization shape 
body_6_16_shape = chrono.ChVisualShapeModelFile() 
body_6_16_shape.SetFilename(shapes_dir +'body_6_16.obj') 
body_6.AddVisualShape(body_6_16_shape, chrono.ChFramed(chrono.ChVector3d(0.283562813036129,0.0147340438210331,0.381), chrono.ChQuaterniond(0.707106781186548,1.00012264708247E-16,-6.07599532411526E-17,0.707106781186547)))

# Visualization shape 
body_6_16_shape = chrono.ChVisualShapeModelFile() 
body_6_16_shape.SetFilename(shapes_dir +'body_6_16.obj') 
body_6.AddVisualShape(body_6_16_shape, chrono.ChFramed(chrono.ChVector3d(0.283562813036129,0.0147340438210331,0.319), chrono.ChQuaterniond(0.707106781186548,1.00012264708247E-16,-6.07599532411526E-17,0.707106781186547)))

# Visualization shape 
body_6_18_shape = chrono.ChVisualShapeModelFile() 
body_6_18_shape.SetFilename(shapes_dir +'body_6_18.obj') 
body_6.AddVisualShape(body_6_18_shape, chrono.ChFramed(chrono.ChVector3d(0.325762813036129,0.0457340438210331,0.35), chrono.ChQuaterniond(0.707106781186548,7.19035069779157E-17,1.24358050357556E-16,0.707106781186547)))

# Visualization shape 
body_5_4_shape = chrono.ChVisualShapeModelFile() 
body_5_4_shape.SetFilename(shapes_dir +'body_5_4.obj') 
body_6.AddVisualShape(body_5_4_shape, chrono.ChFramed(chrono.ChVector3d(0.145195464491374,0.0105340438210331,0.396032651455244), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_5_4_shape = chrono.ChVisualShapeModelFile() 
body_5_4_shape.SetFilename(shapes_dir +'body_5_4.obj') 
body_6.AddVisualShape(body_5_4_shape, chrono.ChFramed(chrono.ChVector3d(0.0531301615808851,0.0105340438210331,0.396032651455244), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_6)



# Rigid body part
body_7 = chrono.ChBodyAuxRef()
body_7.SetName('finger-1')
body_7.SetPos(chrono.ChVector3d(0.156803835692744,-0.646949778295311,0.946869474557972))
body_7.SetRot(chrono.ChQuaterniond(-0.294111916042953,-0.49001496958905,0.541735395870509,0.616365371578586))
body_7.SetMass(0.187774871171945)
body_7.SetInertiaXX(chrono.ChVector3d(0.000265173211229621,0.000196243851432953,0.000294404399300011))
body_7.SetInertiaXY(chrono.ChVector3d(3.78758697241724e-05,-1.32772302928576e-05,6.24458747067537e-05))
body_7.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(0.0144947016631283,0.041295073776454,-0.0448430009100581),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_7_1_shape = chrono.ChVisualShapeModelFile() 
body_7_1_shape.SetFilename(shapes_dir +'body_7_1.obj') 
body_7.AddVisualShape(body_7_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_7)




# Auxiliary marker (coordinate system feature)
marker_0_1 = chrono.ChMarker()
marker_0_1.SetName('base_shoulder')
body_0.AddMarker(marker_0_1)
marker_0_1.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(-0.00675527551769978,-0.886916227898278,-0.0716094107422573),chrono.ChQuaterniond(1,0,0,0)))

# Auxiliary marker (coordinate system feature)
marker_0_2 = chrono.ChMarker()
marker_0_2.SetName('shoulder_bicep')
body_0.AddMarker(marker_0_2)
marker_0_2.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(-0.084532531230816,-0.832366264619319,0.389390589257758),chrono.ChQuaterniond(0.674297403760935,0.212892017889963,0.674297403760937,-0.212892017889964)))

# Auxiliary marker (coordinate system feature)
marker_0_3 = chrono.ChMarker()
marker_0_3.SetName('bicep_elbow')
body_0.AddMarker(marker_0_3)
marker_0_3.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(0.170280911681909,-0.50301333331334,0.539590232820932),chrono.ChQuaterniond(0.674297403760936,0.212892017889963,0.674297403760938,-0.212892017889963)))

# Auxiliary marker (coordinate system feature)
marker_0_4 = chrono.ChMarker()
marker_0_4.SetName('elbow_eef')
body_0.AddMarker(marker_0_4)
marker_0_4.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(0.18654867322731,-0.607820702681636,0.788928691991666),chrono.ChQuaterniond(0.988896061156289,0.120449049094221,-0.0864051294989751,0.0105242766088536)))

# Auxiliary marker (coordinate system feature)
marker_0_5 = chrono.ChMarker()
marker_0_5.SetName('eef_fingers')
body_0.AddMarker(marker_0_5)
marker_0_5.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(0.154257972052283,-0.653860735918741,0.972299534704327),chrono.ChQuaterniond(0.718498983693325,0.141663248953261,0.668086532071762,-0.131723650086051)))
