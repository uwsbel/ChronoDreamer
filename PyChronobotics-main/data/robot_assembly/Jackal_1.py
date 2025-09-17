# PyChrono model automatically generated using Chrono::SolidWorks add-in
# Assembly: C:\Users\Jamiul\Documents\Jackal_IGES_Model\Assem5.SLDASM


import pychrono as chrono 
import builtins 

# Some global settings 
sphereswept_r = 0.001
chrono.ChCollisionModel.SetDefaultSuggestedEnvelope(0.003)
chrono.ChCollisionModel.SetDefaultSuggestedMargin(0.003)
chrono.ChCollisionSystemBullet.SetContactBreakingThreshold(0.002)

shapes_dir = 'Jackal_1_shapes/' 

if hasattr(builtins, 'exported_system_relpath'): 
    shapes_dir = builtins.exported_system_relpath + shapes_dir 

exported_items = [] 

body_0 = chrono.ChBodyAuxRef()
body_0.SetName('SLDW_GROUND')
body_0.SetFixed(True)
exported_items.append(body_0)

# Rigid body part
body_1 = chrono.ChBodyAuxRef()
body_1.SetName('Part16-1')
body_1.SetPos(chrono.ChVector3d(-0.332439884224348,-0.149495387922482,0.519158296825262))
body_1.SetRot(chrono.ChQuaterniond(0.64993714419263,-0.278534932456826,-0.64993714419263,0.278534932456826))
body_1.SetMass(1.08638620302573)
body_1.SetInertiaXX(chrono.ChVector3d(0.00440888720879123,0.00454308632135485,0.00309822478555764))
body_1.SetInertiaXY(chrono.ChVector3d(-0.00137612707325485,-3.78974746569045e-19,1.53492408517995e-19))
body_1.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-1.6139481588162e-17,-4.92324904888469e-18,-0.000156146744304825),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_1_1_shape = chrono.ChVisualShapeModelFile() 
body_1_1_shape.SetFilename(shapes_dir +'body_1_1.obj') 
body_1.AddVisualShape(body_1_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_1)



# Rigid body part
body_2 = chrono.ChBodyAuxRef()
body_2.SetName('Part16-2')
body_2.SetPos(chrono.ChVector3d(-0.332439884224348,-0.149495387922482,0.257158296825262))
body_2.SetRot(chrono.ChQuaterniond(0.584544147097931,0.397879554756904,-0.584544147097931,-0.397879554756904))
body_2.SetMass(1.08638620302573)
body_2.SetInertiaXX(chrono.ChVector3d(0.00346889333505484,0.00548308019509124,0.00309822478555764))
body_2.SetInertiaXY(chrono.ChVector3d(0.000940207900101018,5.74377941495041e-20,-3.13901343760004e-19))
body_2.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-1.6139481588162e-17,-4.92324904888469e-18,-0.000156146744304825),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_1_1_shape = chrono.ChVisualShapeModelFile() 
body_1_1_shape.SetFilename(shapes_dir +'body_1_1.obj') 
body_2.AddVisualShape(body_1_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_2)



# Rigid body part
body_3 = chrono.ChBodyAuxRef()
body_3.SetName('Part15-1')
body_3.SetPos(chrono.ChVector3d(-0.144438239416311,-0.183995387922482,0.388158296825262))
body_3.SetRot(chrono.ChQuaterniond(-1.96261557335472e-17,1.96261557335472e-17,0.707106781186547,0.707106781186548))
body_3.SetMass(6.95740618041676)
body_3.SetInertiaXX(chrono.ChVector3d(0.155701946572891,0.20487956705346,0.0934294924793928))
body_3.SetInertiaXY(chrono.ChVector3d(1.87999088647513e-17,6.50671504690668e-08,1.65461358400414e-17))
body_3.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-3.75028476037096e-17,-2.17505958483275e-17,0.137436231799546),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_3_1_shape = chrono.ChVisualShapeModelFile() 
body_3_1_shape.SetFilename(shapes_dir +'body_3_1.obj') 
body_3.AddVisualShape(body_3_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_3)



# Rigid body part
body_4 = chrono.ChBodyAuxRef()
body_4.SetName('Part16-5')
body_4.SetPos(chrono.ChVector3d(0.0435634053917254,-0.149495387922482,0.519158296825262))
body_4.SetRot(chrono.ChQuaterniond(0.592853063107013,-0.385389732043593,0.592853063107013,-0.385389732043593))
body_4.SetMass(1.08638620302573)
body_4.SetInertiaXX(chrono.ChVector3d(0.00355220841463302,0.00539976511551305,0.00309822478555764))
body_4.SetInertiaXY(chrono.ChVector3d(0.00102218473450571,-2.69031441977384e-19,-1.90463037987575e-19))
body_4.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-1.6139481588162e-17,-4.92324904888469e-18,-0.000156146744304825),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_1_1_shape = chrono.ChVisualShapeModelFile() 
body_1_1_shape.SetFilename(shapes_dir +'body_1_1.obj') 
body_4.AddVisualShape(body_1_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_4)



# Rigid body part
body_5 = chrono.ChBodyAuxRef()
body_5.SetName('Part16-6')
body_5.SetPos(chrono.ChVector3d(0.0435634053917254,-0.149495387922482,0.257158296825262))
body_5.SetRot(chrono.ChQuaterniond(0.00575030040723748,0.707083399639128,0.00575030040723756,0.707083399639128))
body_5.SetMass(1.08638620302573)
body_5.SetInertiaXX(chrono.ChVector3d(0.00585301988054794,0.00309895364959813,0.00309822478555764))
body_5.SetInertiaXY(chrono.ChVector3d(4.48092745273424e-05,-1.56091913622554e-19,-1.71125175516496e-19))
body_5.SetFrameCOMToRef(chrono.ChFramed(chrono.ChVector3d(-1.6139481588162e-17,-4.92324904888469e-18,-0.000156146744304825),chrono.ChQuaterniond(1,0,0,0)))

# Visualization shape 
body_1_1_shape = chrono.ChVisualShapeModelFile() 
body_1_1_shape.SetFilename(shapes_dir +'body_1_1.obj') 
body_5.AddVisualShape(body_1_1_shape, chrono.ChFramed(chrono.ChVector3d(0,0,0), chrono.ChQuaterniond(1,0,0,0)))

exported_items.append(body_5)




# Mate constraint: Concentric1 [MateConcentric] type:1 align:0 flip:False
#   Entity 0: C::E name: body_3 , SW name: Part15-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_1 , SW name: Part16-1 ,  SW ref.type:2 (2)
link_1 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(0.0705617605836886,-0.149495387922482,0.519158296825262)
dA = chrono.ChVector3d(-1,0,5.55111512312578e-17)
cB = chrono.ChVector3d(-0.307441529032385,-0.149495387922482,0.519158296825262)
dB = chrono.ChVector3d(-1,1.79958894003543e-30,5.55111512312588e-17)
link_1.Initialize(body_3,body_1,False,cA,cB,dA,dB)
link_1.SetName("Concentric1")
exported_items.append(link_1)

link_2 = chrono.ChLinkMateGeneric()
link_2.SetConstrainedCoords(True, True, False, False, False, False)
cA = chrono.ChVector3d(0.0705617605836886,-0.149495387922482,0.519158296825262)
cB = chrono.ChVector3d(-0.307441529032385,-0.149495387922482,0.519158296825262)
dA = chrono.ChVector3d(-1,0,5.55111512312578e-17)
dB = chrono.ChVector3d(-1,1.79958894003543e-30,5.55111512312588e-17)
link_2.Initialize(body_3,body_1,False,cA,cB,dA,dB)
link_2.SetName("Concentric1")
exported_items.append(link_2)


# Mate constraint: Concentric2 [MateConcentric] type:1 align:0 flip:False
#   Entity 0: C::E name: body_3 , SW name: Part15-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_2 , SW name: Part16-2 ,  SW ref.type:2 (2)
link_3 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(0.0705617605836886,-0.149495387922482,0.257158296825262)
dA = chrono.ChVector3d(-1,0,5.55111512312578e-17)
cB = chrono.ChVector3d(-0.307441529032385,-0.149495387922482,0.257158296825262)
dB = chrono.ChVector3d(-1,-7.64209001932855e-31,5.55111512312574e-17)
link_3.Initialize(body_3,body_2,False,cA,cB,dA,dB)
link_3.SetName("Concentric2")
exported_items.append(link_3)

link_4 = chrono.ChLinkMateGeneric()
link_4.SetConstrainedCoords(True, True, False, False, False, False)
cA = chrono.ChVector3d(0.0705617605836886,-0.149495387922482,0.257158296825262)
cB = chrono.ChVector3d(-0.307441529032385,-0.149495387922482,0.257158296825262)
dA = chrono.ChVector3d(-1,0,5.55111512312578e-17)
dB = chrono.ChVector3d(-1,-7.64209001932855e-31,5.55111512312574e-17)
link_4.Initialize(body_3,body_2,False,cA,cB,dA,dB)
link_4.SetName("Concentric2")
exported_items.append(link_4)


# Mate constraint: Coincident1 [MateCoincident] type:0 align:0 flip:False
#   Entity 0: C::E name: body_1 , SW name: Part16-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_2 , SW name: Part16-2 ,  SW ref.type:2 (2)
link_5 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.351438239416312,-0.192037484583818,0.478639998345964)
cB = chrono.ChVector3d(-0.351438239416311,-0.094839519151458,0.235610709747247)
dA = chrono.ChVector3d(-1,1.79958894003543e-30,5.55111512312588e-17)
dB = chrono.ChVector3d(-1,-7.64209001932855e-31,5.55111512312574e-17)
link_5.Initialize(body_1,body_2,False,cA,cB,dB)
link_5.SetDistance(0)
link_5.SetName("Coincident1")
exported_items.append(link_5)

link_6 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.351438239416312,-0.192037484583818,0.478639998345964)
dA = chrono.ChVector3d(-1,1.79958894003543e-30,5.55111512312588e-17)
cB = chrono.ChVector3d(-0.351438239416311,-0.094839519151458,0.235610709747247)
dB = chrono.ChVector3d(-1,-7.64209001932855e-31,5.55111512312574e-17)
link_6.Initialize(body_1,body_2,False,cA,cB,dA,dB)
link_6.SetName("Coincident1")
exported_items.append(link_6)


# Mate constraint: Distance1 [MateDistanceDim] type:5 align:0 flip:True
#   Entity 0: C::E name: body_2 , SW name: Part16-2 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_3 , SW name: Part15-1 ,  SW ref.type:2 (2)
link_7 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(-0.351438239416311,-0.094839519151458,0.235610709747247)
cB = chrono.ChVector3d(-0.299438239416311,-0.0339953879224815,0.178158296825262)
dA = chrono.ChVector3d(-1,-7.64209001932855e-31,5.55111512312574e-17)
dB = chrono.ChVector3d(-1,0,5.55111512312578e-17)
link_7.Initialize(body_2,body_3,False,cA,cB,dB)
link_7.SetDistance(0.052)
link_7.SetName("Distance1")
exported_items.append(link_7)

link_8 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(-0.351438239416311,-0.094839519151458,0.235610709747247)
dA = chrono.ChVector3d(-1,-7.64209001932855e-31,5.55111512312574e-17)
cB = chrono.ChVector3d(-0.299438239416311,-0.0339953879224815,0.178158296825262)
dB = chrono.ChVector3d(-1,0,5.55111512312578e-17)
link_8.Initialize(body_2,body_3,False,cA,cB,dA,dB)
link_8.SetName("Distance1")
exported_items.append(link_8)


# Mate constraint: Concentric3 [MateConcentric] type:1 align:1 flip:False
#   Entity 0: C::E name: body_3 , SW name: Part15-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_5 , SW name: Part16-6 ,  SW ref.type:2 (2)
link_9 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(0.0705617605836886,-0.149495387922482,0.257158296825262)
dA = chrono.ChVector3d(-1,0,5.55111512312578e-17)
cB = chrono.ChVector3d(0.0185650501997621,-0.149495387922482,0.257158296825262)
dB = chrono.ChVector3d(1,8.50105477452526e-31,-5.55111512312573e-17)
link_9.SetFlipped(True)
link_9.Initialize(body_3,body_5,False,cA,cB,dA,dB)
link_9.SetName("Concentric3")
exported_items.append(link_9)

link_10 = chrono.ChLinkMateGeneric()
link_10.SetConstrainedCoords(True, True, False, False, False, False)
cA = chrono.ChVector3d(0.0705617605836886,-0.149495387922482,0.257158296825262)
cB = chrono.ChVector3d(0.0185650501997621,-0.149495387922482,0.257158296825262)
dA = chrono.ChVector3d(-1,0,5.55111512312578e-17)
dB = chrono.ChVector3d(1,8.50105477452526e-31,-5.55111512312573e-17)
link_10.Initialize(body_3,body_5,False,cA,cB,dA,dB)
link_10.SetName("Concentric3")
exported_items.append(link_10)


# Mate constraint: Concentric4 [MateConcentric] type:1 align:1 flip:False
#   Entity 0: C::E name: body_3 , SW name: Part15-1 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_4 , SW name: Part16-5 ,  SW ref.type:2 (2)
link_11 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(0.0705617605836886,-0.149495387922482,0.519158296825262)
dA = chrono.ChVector3d(-1,0,5.55111512312578e-17)
cB = chrono.ChVector3d(0.0185650501997621,-0.149495387922482,0.519158296825262)
dB = chrono.ChVector3d(1,-1.83656679496767e-30,-5.55111512312588e-17)
link_11.SetFlipped(True)
link_11.Initialize(body_3,body_4,False,cA,cB,dA,dB)
link_11.SetName("Concentric4")
exported_items.append(link_11)

link_12 = chrono.ChLinkMateGeneric()
link_12.SetConstrainedCoords(True, True, False, False, False, False)
cA = chrono.ChVector3d(0.0705617605836886,-0.149495387922482,0.519158296825262)
cB = chrono.ChVector3d(0.0185650501997621,-0.149495387922482,0.519158296825262)
dA = chrono.ChVector3d(-1,0,5.55111512312578e-17)
dB = chrono.ChVector3d(1,-1.83656679496767e-30,-5.55111512312588e-17)
link_12.Initialize(body_3,body_4,False,cA,cB,dA,dB)
link_12.SetName("Concentric4")
exported_items.append(link_12)


# Mate constraint: Distance2 [MateDistanceDim] type:5 align:0 flip:True
#   Entity 0: C::E name: body_5 , SW name: Part16-6 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_3 , SW name: Part15-1 ,  SW ref.type:2 (2)
link_13 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(0.0625617605836888,-0.150450884283292,0.198416067324634)
cB = chrono.ChVector3d(0.0105617605836887,-0.0339953879224815,0.178158296825262)
dA = chrono.ChVector3d(1,8.50105477452526e-31,-5.55111512312573e-17)
dB = chrono.ChVector3d(1,-8.09304210385054e-33,1.05735526154777e-17)
link_13.Initialize(body_5,body_3,False,cA,cB,dB)
link_13.SetDistance(0.052)
link_13.SetName("Distance2")
exported_items.append(link_13)

link_14 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(0.0625617605836888,-0.150450884283292,0.198416067324634)
dA = chrono.ChVector3d(1,8.50105477452526e-31,-5.55111512312573e-17)
cB = chrono.ChVector3d(0.0105617605836887,-0.0339953879224815,0.178158296825262)
dB = chrono.ChVector3d(1,-8.09304210385054e-33,1.05735526154777e-17)
link_14.Initialize(body_5,body_3,False,cA,cB,dA,dB)
link_14.SetName("Distance2")
exported_items.append(link_14)


# Mate constraint: Distance3 [MateDistanceDim] type:5 align:0 flip:True
#   Entity 0: C::E name: body_4 , SW name: Part16-5 ,  SW ref.type:2 (2)
#   Entity 1: C::E name: body_3 , SW name: Part15-1 ,  SW ref.type:2 (2)
link_15 = chrono.ChLinkMateDistanceZ()
cA = chrono.ChVector3d(0.0625617605836888,-0.0958027093864533,0.543004864117574)
cB = chrono.ChVector3d(0.0105617605836887,-0.0339953879224815,0.178158296825262)
dA = chrono.ChVector3d(1,-1.83656679496767e-30,-5.55111512312588e-17)
dB = chrono.ChVector3d(1,-8.09304210385054e-33,1.05735526154777e-17)
link_15.Initialize(body_4,body_3,False,cA,cB,dB)
link_15.SetDistance(0.052)
link_15.SetName("Distance3")
exported_items.append(link_15)

link_16 = chrono.ChLinkMateParallel()
cA = chrono.ChVector3d(0.0625617605836888,-0.0958027093864533,0.543004864117574)
dA = chrono.ChVector3d(1,-1.83656679496767e-30,-5.55111512312588e-17)
cB = chrono.ChVector3d(0.0105617605836887,-0.0339953879224815,0.178158296825262)
dB = chrono.ChVector3d(1,-8.09304210385054e-33,1.05735526154777e-17)
link_16.Initialize(body_4,body_3,False,cA,cB,dA,dB)
link_16.SetName("Distance3")
exported_items.append(link_16)

