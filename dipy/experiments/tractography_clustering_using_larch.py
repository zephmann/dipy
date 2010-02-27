
from dipy.core import track_metrics as tm
from dipy.viz import fos
from dipy.io import trackvis as tv
from dipy.io import pickle as pkl
from dipy.core import track_performance as pf
import time
import numpy as np


fname='/home/eg01/Data/PBC/pbc2009icdm/brain1/brain1_scan1_fiber_track_mni.trk'

#fname='/home/eg309/Data/PBC/pbc2009icdm/brain1/brain1_scan1_fiber_track_mni.trk'

tree_fname='/home/eg01/Data/tmp/larch_tree.pkl'


print 'Loading file...'
streams,hdr=tv.read(fname)

print 'Copying tracks...'
T=[i[0] for i in streams]

print 'Representing tracks using only 3 pts...'
tracks=[tm.downsample(t,3) for t in T]

print 'Deleting unnecessary data...'
del streams,hdr

print 'LARCH - LocAl Rapid Clustering for tractograpHy ...'
now=time.clock()
C=pf.larch(tracks)
print 'Done in', time.clock()-now,'s.'

print 'Saving Result...'
pkl.save_pickle(tree_fname,C)

'''
l=[]
m=[]

print 'Reducing the number of points...'
T=[pf.approximate_ei_trajectory(t) for t in T]

skel=[]
now=time.clock()
print 'Generate representative tracks... using Zhang'

for c in C:
    
    for d in C[c]['subtree']:        

        print c,d

        l.append(C[c]['subtree'][d]['N'])
        for e in C[c]['subtree'][d]['subtree']:   
         
            m.append(C[c]['subtree'][d]['subtree'][e]['N'])

            #if m[-1]==1:
            tracks_tmp=[T[i] for i in C[c]['subtree'][d]['subtree'][e]['indices']]
            #!!! reference to indices is not correct possibly it would be better to index directly to T
            
            skel.append(tracks_tmp[pf.most_similar_track_zhang(tracks_tmp)[0]])

print 'Done in', time.clock()-now,'s.'

print sum(l),len(l)
print sum(m),len(m)

print len(skel)



r=fos.ren()

fos.add(r,fos.line(skel,fos.red,opacity=1))

fos.show(r)

'''

'''
print 'Reducing the number of points...'
T=[pf.approximate_ei_trajectory(t) for t in T]

print 'Showing initial dataset.'
r=fos.ren()
fos.add(r,fos.line(T,fos.white,opacity=0.1))
fos.show(r)

print 'Showing dataset after clustering.'
fos.clear(r)
colors=np.zeros((len(T),3))
for c in C:
    color=np.random.rand(1,3)
    for i in C[c]['indices']:
        colors[i]=color
fos.add(r,fos.line(T,colors,opacity=1))
fos.show(r)

print 'Some statistics about the clusters'
lens=[len(C[c]['indices']) for c in C]
print 'max ',max(lens), 'min ',min(lens)
    
print 'singletons ',lens.count(1)
print 'doubletons ',lens.count(2)
print 'tripletons ',lens.count(3)

'''



