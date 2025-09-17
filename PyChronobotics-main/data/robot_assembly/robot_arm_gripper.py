# PyChrono model automatically generated using Chrono::SolidWorks add-in
# Assembly: C:\Users\sbel\Downloads\robot_arm_SW\robot_arm_SW\industrial robotic arm_gripper2.SLDASM


import pychrono as chrono 
import builtins 

# Some global settings 
sphereswept_r = 0.001
chrono.ChCollisionModel.SetDefaultSuggestedEnvelope(0.003)
chrono.ChCollisionModel.SetDefaultSuggestedMargin(0.003)
chrono.ChCollisionSystemBullet.SetContactBreakingThreshold(0.002)

shapes_dir = 'robot_arm_gripper_shapes/' 

if hasattr(builtins, 'exported_system_relpath'): 
    shapes_dir = builtins.exported_system_relpath + shapes_dir 

exported_items = [] 

body_0 = chrono.ChBodyAuxRef()
body_0.SetName('SLDW_GROUND')
body_0.SetFixed(True)
exported_items.append(body_0)

# Rigid body part
body_1 = chrono.ChBodyAuxRef()
body_1.SetName('base-1')
body_1.SetPos(chrono.ChVector3d(2.16840434497101e-19,1.38777878078145e-17,-0.00500000000000001))
body_1.SetRot(chrono.ChQuaterniond(0.707106781186547,0.707106781186548,1.67359797579162e-17,1.4141112834892e-17))
body_1.SetMass(6.35815491906364)
body_1.SetInertiaXX(chrono.ChVector3d(0.0325392914519926,0.0440348359439279,0.0425424315033073))
body_1.SetInertiaXY(chrono.ChVector3d(1.76727668893239e-06,0.00216364636786417,-1.19370530475537e-07))
body_1.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(0.0248065992714514,0.0914537839283252,-3.63390074177685e-06),chrono.ChQuaterniond(1,0,0,0)))
body_1.SetFixed(True)

# Visualization shape 
body_1_1_mesh = chrono.ChTriangleMeshConnected()
body_1_1_mesh.LoadWavefrontMesh(shapes_dir + 'body_1_1.obj', False, True)

body_1_1_shape = chrono.ChVisualShapeTriangleMesh()
body_1_1_shape.SetMesh(body_1_1_mesh)
body_1_1_shape.SetName("body_1_1.obj")
body_1_1_shape.SetMutable(False)

body_1.AddVisualShape(body_1_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_1)



# Rigid body part
body_2 = chrono.ChBodyAuxRef()
body_2.SetName('wrist-1')
body_2.SetPos(chrono.ChVector3d(0.645059159036666,-0.699252755768097,-0.105787924816399))
body_2.SetRot(chrono.ChQuaterniond(0.669328561438042,-0.286230234959453,0.646585069882577,0.228033499388315))
body_2.SetMass(0.690905359894318)
body_2.SetInertiaXX(chrono.ChVector3d(0.00268219061493006,0.00120876425218994,0.00187632381803341))
body_2.SetInertiaXY(chrono.ChVector3d(0.000129706422527919,-7.02128623656765e-05,0.00080526820598089))
body_2.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.731419039863804,0.584005934529981,-3.70207795692633e-05),chrono.ChQuaterniond(1,0,0,0)))


# Visualization shape
body_2_1_mesh = chrono.ChTriangleMeshConnected()
body_2_1_mesh.LoadWavefrontMesh(shapes_dir + 'body_2_1.obj', False, True)
body_2_1_shape = chrono.ChVisualShapeTriangleMesh()
body_2_1_shape.SetMesh(body_2_1_mesh)
body_2_1_shape.SetName("body_2_1.obj")
body_2_1_shape.SetMutable(False)
body_2.AddVisualShape(body_2_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.689574061929817,0.568745872962511,7.93270177692674E-17), chrono.ChQuaterniond(-2.930393114694E-17,0.137196723577704,0.99054381984824,-5.40535866929113E-17)))

# Visualization shape 
body_2_2_mesh = chrono.ChTriangleMeshConnected()
body_2_2_mesh.LoadWavefrontMesh(shapes_dir + 'body_2_2.obj', False, True)
body_2_2_shape = chrono.ChVisualShapeTriangleMesh()
body_2_2_shape.SetMesh(body_2_2_mesh)
body_2_2_shape.SetName("body_2_2.obj")
body_2_2_shape.SetMutable(False)
body_2.AddVisualShape(body_2_2_shape, chrono.ChFramed(chrono.ChVector3d(-0.778110640793093,0.593751356424883,2.85488682303067E-17), chrono.ChQuaterniond(0.700420252077117,-0.0970127335983713,-0.700420252077116,-0.0970127335983712)))

exported_items.append(body_2)



# Rigid body part
body_3 = chrono.ChBodyAuxRef()
body_3.SetName('finger_1-1')
body_3.SetPos(chrono.ChVector3d(0.164221384674298,-0.181254876896152,0.737774543732092))
body_3.SetRot(chrono.ChQuaterniond(0.396147545149487,0.161904861648937,0.68832173856013,0.585719320555532))
body_3.SetMass(0.0938874355859725)
body_3.SetInertiaXX(chrono.ChVector3d(3.31466514037026e-05,2.45304814291191e-05,3.68005499125014e-05))
body_3.SetInertiaXY(chrono.ChVector3d(4.73448371552155e-06,-1.6596537866072e-06,7.80573433834422e-06))
body_3.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(0.00724735083156416,0.020647536888227,-0.022421500455029),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape
body_3_1_mesh = chrono.ChTriangleMeshConnected()
body_3_1_mesh.LoadWavefrontMesh(shapes_dir + 'body_3_1.obj', False, True)
body_3_1_shape = chrono.ChVisualShapeTriangleMesh()
body_3_1_shape.SetMesh(body_3_1_mesh)
body_3_1_shape.SetName("body_3_1.obj")
body_3_1_shape.SetMutable(False)
body_3.AddVisualShape(body_3_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

# Collision shape
contact_material = chrono.ChContactMaterialSMC()
body_3_1_collision_shape = chrono.ChCollisionShapeTriangleMesh(contact_material, body_3_1_mesh, False, False, 0.001)
body_3.AddCollisionShape(body_3_1_collision_shape)
body_3.GetCollisionModel().SetFamily(2)
body_3.EnableCollision(True)

exported_items.append(body_3)



# Rigid body part
body_4 = chrono.ChBodyAuxRef()
body_4.SetName('endoffactor-1')
body_4.SetPos(chrono.ChVector3d(0.167160165846067,-0.181196645672621,0.734309710248563))
body_4.SetRot(chrono.ChQuaterniond(0.396147545149489,0.161904861648939,0.688321738560128,0.585719320555532))
body_4.SetMass(0.38232347669012)
body_4.SetInertiaXX(chrono.ChVector3d(0.000560005407272658,0.000562334354846062,0.000200649640246989))
body_4.SetInertiaXY(chrono.ChVector3d(6.41346215573423e-10,1.55107482746673e-07,-1.57001286264211e-06))
body_4.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(1.94804546979808e-07,-0.0397712704827772,7.29741759192392e-05),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape
body_4_1_mesh = chrono.ChTriangleMeshConnected()
body_4_1_mesh.LoadWavefrontMesh(shapes_dir + 'body_4_1.obj', False, True)
body_4_1_shape = chrono.ChVisualShapeTriangleMesh()
body_4_1_shape.SetMesh(body_4_1_mesh)
body_4_1_shape.SetName("body_4_1.obj")
body_4_1_shape.SetMutable(False)

body_4.AddVisualShape(body_4_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

# Collision shape
contact_material = chrono.ChContactMaterialSMC()
body_4.AddCollisionShape(chrono.ChCollisionShapeBox(contact_material,0.05,0.03,0.05))
body_4.EnableCollision(True)
body_4.GetCollisionModel().SetFamily(3)
body_4.GetCollisionModel().DisallowCollisionsWith(2)
exported_items.append(body_4)



# Rigid body part
body_5 = chrono.ChBodyAuxRef()
body_5.SetName('elbow-1')
body_5.SetPos(chrono.ChVector3d(0.645730580540764,-0.699980585658496,-0.104827756846103))
body_5.SetRot(chrono.ChQuaterniond(0.669500769701939,-0.286718989121477,0.646368487224709,0.227527403555068))
body_5.SetMass(9.52797805618334)
body_5.SetInertiaXX(chrono.ChVector3d(0.169395944649557,0.104661165748131,0.122840410803669))
body_5.SetInertiaXY(chrono.ChVector3d(0.0137683876912721,-0.00740007428752607,0.0595917633440791))
body_5.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.401489686180518,0.533180567480613,-0.00882152577968123),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_5_1_shape = chrono.ChVisualShapeModelFile() 
body_5_1_shape.SetFilename(shapes_dir +'body_5_1.obj')

body_5_1_mesh = chrono.ChTriangleMeshConnected()
body_5_1_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_1.obj', False, True)
body_5_1_shape = chrono.ChVisualShapeTriangleMesh()
body_5_1_shape.SetMesh(body_5_1_mesh)
body_5_1_shape.SetName("body_5_1.obj")
body_5_1_shape.SetMutable(False)

body_5.AddVisualShape(body_5_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.543321144291398,0.619181847628244,-0.0150000000000001), chrono.ChQuaterniond(0.973742326368847,-3.31770475511386E-17,-0.227652985567477,2.78735090970301E-17)))

# Visualization shape
body_5_1_mesh = chrono.ChTriangleMeshConnected()
body_5_1_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_1.obj', False, True)
body_5_1_shape = chrono.ChVisualShapeTriangleMesh()
body_5_1_shape.SetMesh(body_5_1_mesh)
body_5_1_shape.SetName("body_5_1.obj")
body_5_1_shape.SetMutable(False)

body_5.AddVisualShape(body_5_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.543321144291398,0.619181847628244,0.015), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape
body_5_3_mesh = chrono.ChTriangleMeshConnected()
body_5_3_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_3.obj', False, True)
body_5_3_shape = chrono.ChVisualShapeTriangleMesh()
body_5_3_shape.SetMesh(body_5_3_mesh)
body_5_3_shape.SetName("body_5_3.obj")
body_5_3_shape.SetMutable(False)

body_5.AddVisualShape(body_5_3_shape, chrono.ChFramed(chrono.ChVector3d(-0.220483525785213,0.223688426635067,-1.09910271764937E-16), chrono.ChQuaterniond(0.991366672698128,-6.1985962210009E-17,-8.93446565697906E-18,0.13111872583061)))

# Visualization shape
body_5_4_mesh = chrono.ChTriangleMeshConnected()
body_5_4_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_4.obj', False, True)
body_5_4_shape = chrono.ChVisualShapeTriangleMesh()
body_5_4_shape.SetMesh(body_5_4_mesh)
body_5_4_shape.SetName("body_5_4.obj")
body_5_4_shape.SetMutable(False)

body_5.AddVisualShape(body_5_4_shape, chrono.ChFramed(chrono.ChVector3d(-0.124922519257827,-0.0650596762319681,7.32122992828801E-17), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape
body_5_5_mesh = chrono.ChTriangleMeshConnected()
body_5_5_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_5.obj', False, True)
body_5_5_shape = chrono.ChVisualShapeTriangleMesh()
body_5_5_shape.SetMesh(body_5_5_mesh)
body_5_5_shape.SetName("body_5_5.obj")
body_5_5_shape.SetMutable(False)

body_5.AddVisualShape(body_5_5_shape, chrono.ChFramed(chrono.ChVector3d(-0.0791099203362491,-0.0726105246150223,4.79483428995232E-17), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape
body_5_6_mesh = chrono.ChTriangleMeshConnected()
body_5_6_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_6.obj', False, True)
body_5_6_shape = chrono.ChVisualShapeTriangleMesh()
body_5_6_shape.SetMesh(body_5_6_mesh)
body_5_6_shape.SetName("body_5_6.obj")
body_5_6_shape.SetMutable(False)

body_5.AddVisualShape(body_5_6_shape, chrono.ChFramed(chrono.ChVector3d(-0.22048352578521,0.223688426635073,1.11203069757645E-18), chrono.ChQuaterniond(0.991366672698128,-4.64135861760645E-17,-1.34462793624774E-17,0.13111872583061)))

# Visualization shape
body_5_7_mesh = chrono.ChTriangleMeshConnected()
body_5_7_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_7.obj', False, True)
body_5_7_shape = chrono.ChVisualShapeTriangleMesh()
body_5_7_shape.SetMesh(body_5_7_mesh)
body_5_7_shape.SetName("body_5_7.obj")
body_5_7_shape.SetMutable(False)

body_5.AddVisualShape(body_5_7_shape, chrono.ChFramed(chrono.ChVector3d(0.453436171818078,-0.0650596762319678,8.2525331492937E-17), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape
body_5_8_mesh = chrono.ChTriangleMeshConnected()
body_5_8_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_8.obj', False, True)
body_5_8_shape = chrono.ChVisualShapeTriangleMesh()
body_5_8_shape.SetMesh(body_5_8_mesh)
body_5_8_shape.SetName("body_5_8.obj")
body_5_8_shape.SetMutable(False)

body_5.AddVisualShape(body_5_8_shape, chrono.ChFramed(chrono.ChVector3d(-0.0767998869238414,-0.0844119866991259,4.72507707018854E-17), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_5)



# Rigid body part
body_6 = chrono.ChBodyAuxRef()
body_6.SetName('finger_2-1')
body_6.SetPos(chrono.ChVector3d(0.163747773587517,-0.183140392606903,0.738293897476684))
body_6.SetRot(chrono.ChQuaterniond(0.396147545149489,0.161904861648939,0.688321738560128,0.585719320555532))
body_6.SetMass(0.0938874355859725)
body_6.SetInertiaXX(chrono.ChVector3d(3.31467659305197e-05,2.45303153855084e-05,3.6800601429295e-05))
body_6.SetInertiaXY(chrono.ChVector3d(-4.73444367209372e-06,-1.65947246859143e-06,-7.80569347513243e-06))
body_6.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.00724737975140957,0.0206478134281555,0.0224215440569809),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape
body_6_1_mesh = chrono.ChTriangleMeshConnected()
body_6_1_mesh.LoadWavefrontMesh(shapes_dir + 'body_6_1.obj', False, True)
body_6_1_shape = chrono.ChVisualShapeTriangleMesh()
body_6_1_shape.SetMesh(body_6_1_mesh)
body_6_1_shape.SetName("body_6_1.obj")
body_6_1_shape.SetMutable(False)
body_6.AddVisualShape(body_6_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

# Collision shape
contact_material = chrono.ChContactMaterialSMC()
body_6_1_collision_shape = chrono.ChCollisionShapeTriangleMesh(contact_material, body_6_1_mesh, False, False, 0.001)
body_6.AddCollisionShape(body_6_1_collision_shape)
body_6.GetCollisionModel().SetFamily(2)
body_6.EnableCollision(True)

exported_items.append(body_6)



# Rigid body part
body_7 = chrono.ChBodyAuxRef()
body_7.SetName('shoulder-1')
body_7.SetPos(chrono.ChVector3d(6.4401609045639e-17,0,-0.00500000000000003))
body_7.SetRot(chrono.ChQuaterniond(0.2837030775802,0.283703077580201,0.647697895450898,0.647697895450899))
body_7.SetMass(6.19175613601669)
body_7.SetInertiaXX(chrono.ChVector3d(0.0350922385122827,0.0337273308671819,0.0439040844700944))
body_7.SetInertiaXY(chrono.ChVector3d(0.0019273179786921,0.00478177280373868,9.8141544031982e-05))
body_7.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.0470728043239676,0.2783213608153,-0.0152778527555248),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape
body_7_1_mesh = chrono.ChTriangleMeshConnected()
body_7_1_mesh.LoadWavefrontMesh(shapes_dir + 'body_7_1.obj', False, True)
body_7_1_shape = chrono.ChVisualShapeTriangleMesh()
body_7_1_shape.SetMesh(body_7_1_mesh)
body_7_1_shape.SetName("body_7_1.obj")
body_7_1_shape.SetMutable(False)

body_7.AddVisualShape(body_7_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape
body_7_2_mesh = chrono.ChTriangleMeshConnected()
body_7_2_mesh.LoadWavefrontMesh(shapes_dir + 'body_7_2.obj', False, True)
body_7_2_shape = chrono.ChVisualShapeTriangleMesh()
body_7_2_shape.SetMesh(body_7_2_mesh)
body_7_2_shape.SetName("body_7_2.obj")
body_7_2_shape.SetMutable(False)

body_7.AddVisualShape(body_7_2_shape, chrono.ChFramed(chrono.ChVector3d(-2.29766513046727E-18,0.150481497931565,9.75774393987111E-18), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_5_3_mesh = chrono.ChTriangleMeshConnected()
body_5_3_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_3.obj', False, True)
body_5_3_shape = chrono.ChVisualShapeTriangleMesh()
body_5_3_shape.SetMesh(body_5_3_mesh)
body_5_3_shape.SetName("body_5_3.obj")
body_5_3_shape.SetMutable(False)

body_7.AddVisualShape(body_5_3_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_5_6_mesh = chrono.ChTriangleMeshConnected()
body_5_6_mesh.LoadWavefrontMesh(shapes_dir + 'body_5_6.obj', False, True)
body_5_6_shape = chrono.ChVisualShapeTriangleMesh()
body_5_6_shape.SetMesh(body_5_6_mesh)
body_5_6_shape.SetName("body_5_6.obj")
body_5_6_shape.SetMutable(False)

body_7.AddVisualShape(body_5_6_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_7)



# Rigid body part
body_8 = chrono.ChBodyAuxRef()
body_8.SetName('biceps-1')
body_8.SetPos(chrono.ChVector3d(0.0699735756613435,0.333994598624203,0.181455961876339))
body_8.SetRot(chrono.ChQuaterniond(-0.0320607086156751,0.540938743674528,0.455395735148918,0.706379579944849))
body_8.SetMass(2.5112345103127)
body_8.SetInertiaXX(chrono.ChVector3d(0.0343916532907699,0.0215578494505111,0.050795577371841))
body_8.SetInertiaXY(chrono.ChVector3d(0.0239277925334137,0.00195758086845376,-0.00255173368706076))
body_8.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-0.217022834717045,0.414372371507996,-0.154802287341841),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_8_1_mesh = chrono.ChTriangleMeshConnected()
body_8_1_mesh.LoadWavefrontMesh(shapes_dir + 'body_8_1.obj', False, True)
body_8_1_shape = chrono.ChVisualShapeTriangleMesh()
body_8_1_shape.SetMesh(body_8_1_mesh)
body_8_1_shape.SetName("body_8_1.obj")
body_8_1_shape.SetMutable(False)

body_8.AddVisualShape(body_8_1_shape, chrono.ChFramed(chrono.ChVector3d(-0.227161101767331,0.42397977678273,2.77555756156289E-16), chrono.ChQuaterniond(0.918653832476948,-6.36982183537584E-17,-2.50980166887015E-17,0.395063458289191)))

# Visualization shape 
body_8_2_mesh = chrono.ChTriangleMeshConnected()
body_8_2_mesh.LoadWavefrontMesh(shapes_dir + 'body_8_2.obj', False, True)
body_8_2_shape = chrono.ChVisualShapeTriangleMesh()
body_8_2_shape.SetMesh(body_8_2_mesh)
body_8_2_shape.SetName("body_8_2.obj")
body_8_2_shape.SetMutable(False)

body_8.AddVisualShape(body_8_2_shape, chrono.ChFramed(chrono.ChVector3d(0.0593547632575068,0.0212044641075161,0.000753926210741218), chrono.ChQuaterniond(0.99251448470166,-4.94337686032854E-17,-1.21237539944481E-17,0.122126973504618)))

exported_items.append(body_8)


# Auxiliary marker (coordinate system feature)
marker_0_1 = chrono.ChMarker()
marker_0_1.SetName('MARKER_1')
body_0.AddMarker(marker_0_1)
marker_0_1.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(4.96640263017766E-19,-2.41661115592717E-17,0.166),chrono.ChQuaterniond(1,0,0,0)))

# Auxiliary marker (coordinate system feature)
marker_0_2 = chrono.ChMarker()
marker_0_2.SetName('MARKER_6')
body_0.AddMarker(marker_0_2)
marker_0_2.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(0.163144434816736,-0.176850749323825,0.749857465007985),chrono.ChQuaterniond(0.658599944034038,0.257383204033133,-0.658599944034039,0.257383204033134)))

# Auxiliary marker (coordinate system feature)
marker_0_3 = chrono.ChMarker()
marker_0_3.SetName('MARKER_2')
body_0.AddMarker(marker_0_3)
marker_0_3.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(0.128143763594464,-0.00717118203968383,0.289000000000001),chrono.ChQuaterniond(0.658599944034039,0.257383204033133,-0.658599944034038,0.257383204033133)))

# Auxiliary marker (coordinate system feature)
marker_0_4 = chrono.ChMarker()
marker_0_4.SetName('MARKER_3')
body_0.AddMarker(marker_0_4)
marker_0_4.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(0.362644487337514,-0.258165724788785,0.233971409220554),chrono.ChQuaterniond(0.658599944034038,0.257383204033133,-0.658599944034039,0.257383204033133)))

# Auxiliary marker (coordinate system feature)
marker_0_5 = chrono.ChMarker()
marker_0_5.SetName('MARKER_4')
body_0.AddMarker(marker_0_5)
marker_0_5.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(0.235775059022449,-0.213551034674038,0.549578249426805),chrono.ChQuaterniond(0.658599944034039,0.257383204033133,-0.658599944034038,0.257383204033133)))

# Auxiliary marker (coordinate system feature)
marker_0_6 = chrono.ChMarker()
marker_0_6.SetName('MARKER_5')
body_0.AddMarker(marker_0_6)
marker_0_6.ImposeAbsoluteTransform(chrono.ChFramed(chrono.ChVector3d(0.187815261716513,-0.203594255644253,0.654253797639965),chrono.ChQuaterniond(0.983374673352811,-0.130821427139734,-0.124836692034385,-0.0166074179596879)))
