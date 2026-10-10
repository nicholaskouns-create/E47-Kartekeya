import numpy as np
from scipy.spatial import HalfspaceIntersection, ConvexHull
from collections import Counter
labels=[]; normals=[]
for J, js in [(2,list(range(5))),(5,[3,4])]:
 for r,j12 in enumerate(js):
  for m in range(-J,J+1):
   z=m/(J+1); phi=2*np.pi*(r/len(js)+m/47+(0 if J==2 else 1/94))
   normals.append([np.sqrt(1-z*z)*np.cos(phi),np.sqrt(1-z*z)*np.sin(phi),z]); labels.append((J,j12,m))
normals=np.array(normals)
verts=HalfspaceIntersection(np.column_stack((normals,-np.ones(47))),np.zeros(3)).intersections
hull=ConvexHull(verts)
radii=np.linalg.norm(verts,axis=1)
vol=hull.volume; area=hull.area; sph=np.pi**(1/3)*(6*vol)**(2/3)/area
rad=2/(1+radii.max()) # 1-(R-r)/(R+r)
faces=[]
for n in normals:
 faces.append(np.where(np.isclose(verts@n,1,atol=1e-8))[0])
edgecount=sum(map(len,faces))//2
print('vertices',len(verts),'edges',edgecount,'faces',len(faces),'face_sizes',dict(sorted(Counter(map(len,faces)).items())))
for k,v in [('rmin',radii.min()),('rmax',radii.max()),('rmean',radii.mean()),('rstd_population',radii.std()),('volume',vol),('area',area),('sphere_area_equal_volume',4*np.pi*(3*vol/(4*np.pi))**(2/3)),('sphericity',sph),('radial_sphericity',rad),('R_over_r',radii.max()),('surface_excess_percent',(1/sph-1)*100),('equal_volume_radius',(3*vol/(4*np.pi))**(1/3)),('min_facet_slack',np.min(1-verts@normals.T))]: print(k,format(v,'.12f'))
np.savez('/mnt/data/e47_measured_geometry.npz',vertices=verts,normals=normals,labels=np.array(labels),radii=radii)
