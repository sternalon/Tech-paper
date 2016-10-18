#!/usr/bin/env python

#First import the netcdf4 library
from netCDF4 import Dataset  # http://code.google.com/p/netcdf4-python/
import numpy as np  # http://code.google.com/p/netcdf4-python/
import matplotlib
import math
import os
matplotlib.use("GTKAgg")
from pylab import *
#import matplotlib.pyplot as plt
import pdb
import netCDF4 as nc
import sys
import argparse
from m6toolbox  import section2quadmesh


def transpose_matrix(data):
	M=data.shape
	data_new=np.zeros([M[1],M[0]])
	for i in range(M[0]):
		for j in range(M[1]):
			data_new[j,i]=data[i,j]
	#print 'After rotation' ,data.shape
	return data_new


def mask_grounded_ice(data,depth,base):
   """
   Mask regions where the ice shelf is grounded (base>=depth). Works with 2D or 3D arrays.
   """
   if len(data.shape) == 2: # 2D array
      data = np.ma.masked_where(base+1.0>=depth, data) # need +1 here      
   else: # 3D array
      NZ,NY,NX = data.shape
      base = np.resize(base,(NZ,NY,NX))
      depth = np.resize(depth,(NZ,NY,NX))
      data = np.ma.masked_where(base+1.0>=depth, data) # need +1 here

   return data

def mask_ocean(data,area):
   """
   Mask open ocean. Works with 2D or 3D arrays.
   """
   if len(data.shape) == 2: # 2D array
     data = np.ma.masked_where(area==0,data)
     #data[np.where(area==0)]=np.nan

   else: # 3D array
     NZ,NY,NX = data.shape
     area=np.resize(area,(NZ,NY,NX))
     data = np.ma.masked_where(area==0,data)

   return  data

def get_psi2D(u,v):
    '''
    Loop in time and compute the barotropic streamfunction psi at h points.
    '''
    NT,NY,NX = u.shape
    uh = np.zeros(u.shape); vh = np.zeros(v.shape); psi = np.zeros(u.shape)
    # u and v at h points
    utmp = 0.5 * (u[:,:,0:-1] + u[:,:,1::]) #u_i = 0.5(u_(i+0.5) + u_(i-0.5))
    vtmp = 0.5 * (v[:,0:-1,:] + v[:,1::,:]) #v_j = 0.5(v_(j+0.5) + v_(j-0.5))
    uh[:,:,1::] = utmp; uh[:,:,0] = 0.5*u[:,:,0] #u_i=1 = 0.5*u_(i=3/2)
    vh[:,1::,:] = vtmp; vh[:,0,:] = 0.5*v[:,0,:] #v_j=1 = 0.5*v_(j=3/2)
    for t in range(NT):
        psi[t,:,:] = (-uh[t,:,:].cumsum(axis=0) + vh[t,:,:].cumsum(axis=1))*0.5
        
    return psi 

def squeeze_matrix_to_2D(data,time_slice,time_slice_num,direction=None,dir_slice=None, dir_slice_num=None):
	#This routine reduces the data to two dimensions. It assumes that the first dimension is time. 
	#The time_slice / time_slice_num must be provided to tell where the averages should be applied.
	#If there are three spatial dimensions, then the dirction, and dir_slice, dir_slice_num must be added

	#Trimming and squeezing the data

	#Reducing time dimension  - assumes that first dim is time.
	if time_slice=='mean':
		data=np.squeeze(np.mean(data,axis=0))  #Mean over first variable
	else:
		if len(data.shape) == 3:
			data=np.squeeze(data[time_slice_num,:,:])  #Mean over first variable
		if len(data.shape) == 4:
			data=np.squeeze(data[time_slice_num,:,:,:])  #Mean over first variable


	if len(data.shape) == 3:
		if dir_slice=='mean':
 			if direction=='xy':
				axis_num=0
 			if direction=='xz':
				axis_num=1
 			if direction=='yz':
				axis_num=2
			data=np.squeeze(np.mean(data,axis=axis_num))
		else:
 			if direction=='xy':
				data=np.squeeze(data[dir_slice_num,:,:])
 			if direction=='xz':
				data=np.squeeze(data[:,dir_slice_num,:])
 			if direction=='yz':
				data=np.squeeze(data[:,:,dir_slice_num])
				
	return data


def load_data_from_file(filename, field, time_slice, time_slice_num, direction=None ,dir_slice=None, dir_slice_num=None):
	with nc.Dataset(filename) as file:
		data = file.variables[field][:]

	#Give an error message if direction is not given for 4D matrix	
	if (len(data.shape)>3 and direction is None):
		print 'Direction must be provided for 4-dim matrix'
		return
	data=squeeze_matrix_to_2D(data,time_slice,time_slice_num,direction,dir_slice, dir_slice_num)

	return data

def calculate_barotropic_streamfunction(filename,depth,ice_base,time_slice=None,time_slice_num=-1):
	uhbt = Dataset(filename).variables['uhbt'][:]
	vhbt = Dataset(filename).variables['vhbt'][:]
	# mask grouded region
	uhbt = mask_grounded_ice(uhbt,depth,ice_base)
	vhbt = mask_grounded_ice(vhbt,depth,ice_base)
	psi2D = get_psi2D(uhbt,vhbt)
	psi2D = mask_grounded_ice(psi2D,depth,ice_base)
	#saveXY(psi2D,'barotropicStreamfunction')

	#Taking only final value
	psi2D=squeeze_matrix_to_2D(psi2D,time_slice,time_slice_num)

	return psi2D
	
def get_horizontal_dimentions(filename,start_from_zero=False):
	with nc.Dataset(filename) as file:
		x = file.variables['xq'][:]
		y = file.variables['yh'][:]
	if start_from_zero is True:
		x=x-np.min(x)
		y=y-np.min(y)
	print np.max(y),np.max(x)
	return [x,y]

def get_vertical_dimentions(filename, vertical_coordinate, time_slice, time_slice_num, direction ,dir_slice, dir_slice_num):
	if vertical_coordinate=='z':
		with nc.Dataset(filename) as file:
			z = file.variables['zt'][:]
		return z
	if vertical_coordinate=='layers':
		z=load_data_from_file(filename, 'e' , time_slice, time_slice_num, direction ,dir_slice, dir_slice_num)

	return z


def load_static_variables(ocean_geometry_filename,ice_geometry_filename,ISOMIP_IC_filename):
	# bedrock
	depth = Dataset(ocean_geometry_filename).variables['D'][:]
	# area under shelf 
	shelf_area = Dataset(ice_geometry_filename).variables['area'][:,:]
	# base of STATIC ice shelf, which is ssh(t=0); make it positive
	ice_base = -Dataset(ISOMIP_IC_filename).variables['ave_ssh'][0,:,:]
	ice_base[ice_base<1e-5] = 0.0
	#mask grounded ice and open ocean
	shelf_area = mask_grounded_ice(shelf_area,depth,ice_base) 
	shelf_area = mask_ocean(shelf_area,shelf_area)

	# x,y, at tracer points 
	x=Dataset(ocean_geometry_filename).variables['geolon'][:]#*1.0e3 # in m
	y=Dataset(ocean_geometry_filename).variables['geolat'][:]#*1.0e3 # in m
	xvec=Dataset(ocean_geometry_filename).variables['lonh'][:]#*1.0e3 # in m
	yvec=Dataset(ocean_geometry_filename).variables['lath'][:]#*1.0e3 # in m
	return [depth, shelf_area, ice_base, x,y, xvec, yvec]


def plot_data_field(data,x,y,field,vmin=None,vmax=None,rotated=False,colorbar=True,cmap='jet',title='',xlabel='',ylabel=''): 
	if rotated is True:
		data=transpose_matrix(data)
		tmp=y ; y=x ; x=tmp
		x=transpose_matrix(x)
		y=transpose_matrix(y)
	print 'Starting to plot...'	
	if vmin==None:
		vmin=np.min(data)
	else:
		vmin=float(vmin)

	if vmax==None:
		vmax=np.max(data)
	else:
		vmax=float(vmax)

	cNorm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
	#cNorm = mpl.colors.Normalize(vmin=600, vmax=850)
	plt.pcolormesh(x,y,data,norm=cNorm,cmap=cmap)
	if colorbar is True:
		plt.colorbar()
	#plt.xlim(np.min(x),np.max(x))
	xmin=430  ;xmax=670
	plt.xlim(xmin,xmax)
	plt.ylim(np.min(y),np.max(y))
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	#plt.grid(True)
	plt.title(title)


def interpolated_onto_vertical_grid(data, layer_interface, x, vertical_coordinate):
	if vertical_coordinate=='layers':  
                representation='linear'  #'pcm'
                #representation='pcm'
                M=layer_interface.shape
                layers=range(0,M[0]-1)
                q=data[range(0,M[0]-1),:] ;q=q[:,range(0,len(x)-1) ]
                layer_interface=layer_interface[:,range(0,len(x)-1)]
                (X, Z, Q)=section2quadmesh(x, layer_interface, q, representation)
        if vertical_coordinate=='z':
                X=x
                Z=-layer_interface
                Q=data

	return [X,Z,Q]


##########################################################  Main Program   #########################################################################
####################################################################################################################################################

def main():
	parser = argparse.ArgumentParser()
        parser.add_argument('--file1', default=None, help='The input data file1 in NetCDF format.')
        parser.add_argument('--file2', default=None, help='The input data file2 in NetCDF format.')
        parser.add_argument('--field', default=None, help='Feild to plot')
        parser.add_argument('--field2', default=None, help='Feild to plot')
        parser.add_argument('--operation',default=None, help='Operation betweeen fields')
        parser.add_argument('--vmax', default=None, help='Maximum for plotting')
        parser.add_argument('--vmin', default=None, help='Minimum for plotting')
        parser.add_argument('--rotated', default=None, help='Minimum for plotting')
	args = parser.parse_args()


	#Plotting flats
	save_figure=True


	#What to plot?


	#Defining path
	Berg_path='/lustre/f1/unswept/Alon.Stern/MOM6-examples_Alon/ice_ocean_SIS2/Tech_ISOMIP/Bergs/Melt_on_high_melt_with_decay/'
	Berg_path_init='/lustre/f1/unswept/Alon.Stern/MOM6-examples_Alon/ice_ocean_SIS2/Tech_ISOMIP/Bergs/Melt_on_high_melt_with_decay_initialize/'

	#Geometry files
	ocean_geometry_filename=Berg_path +'ocean_geometry.nc'
	ice_geometry_filename=Berg_path+'/MOM_Shelf_IC.nc'
	ISOMIP_IC_filename=Berg_path+'ISOMIP_IC.nc'
	
	#Berg files
	#Berg_ocean_file_init=Berg_path_init+'00010101.ocean_month.nc'
	Berg_ocean_file_init=Berg_path+'00010101.ocean_month.nc'
	Berg_ocean_file=Berg_path+'00060101.ocean_month.nc'

	Berg_ocean_file='/lustre/f1/unswept/Alon.Stern/MOM6-examples_Alon/ice_ocean_SIS2/Tech_ISOMIP/Bergs/completed/Melt_on_with_decay/'+ '00010101.ocean_month.nc'

	#Load static fields
	(depth, shelf_area, ice_base, x,y, xvec, yvec)=load_static_variables(ocean_geometry_filename,ice_geometry_filename,ISOMIP_IC_filename)	
	
	#Defining figure characteristics
	fig=plt.figure(figsize=(15,10),facecolor='grey')
	#fig = plt.figure(facecolor='black')
	ax = fig.add_subplot(111,axisbg='gray')


	time_slice_num=np.array([1,10,-1])
	for n in range(3):
		plot_anomaly=True
		vertical_coordinate='layers'  #'z'
		#vertical_coordinate='z'
		time_slice=None
		#field='u'  ; vmin=-0.2  ; vmax=0.2    ; vanom=0.3
		field='temp'  ; vmin=-1.0  ; vmax=5.0 ; vanom=0.3
		#field='salt'  ; vmin=34  ; vmax=34.7  ;vdiff=0.05  ; vanom=0.05
		if n==0:
			#filename1=Berg_ocean_file_init
			filename1=Berg_ocean_file
		else:
			filename1=Berg_ocean_file
		
		if vertical_coordinate=='z':
			filename1=filename1.split('.nc')[0] + '_z.nc'

		print filename1

		data1=load_data_from_file(filename1,field , time_slice, time_slice_num=time_slice_num[n], direction='xz' ,dir_slice=None, dir_slice_num=20)
		elevation1 = get_vertical_dimentions(filename1,vertical_coordinate, time_slice, time_slice_num=time_slice_num[n], direction='xz' ,dir_slice=None, dir_slice_num=20)
		(x1 ,z1 ,data1) =interpolated_onto_vertical_grid(data1, elevation1, xvec, vertical_coordinate)

		if plot_anomaly is True:
			data0=load_data_from_file(filename1,field , time_slice=None, time_slice_num=0, direction='xz' ,dir_slice=None, dir_slice_num=20)
			elevation0 = get_vertical_dimentions(filename1,vertical_coordinate, time_slice=None, time_slice_num=-1, direction='xz' ,dir_slice=None, dir_slice_num=20)
			(x0 ,z0 ,data0) =interpolated_onto_vertical_grid(data0, elevation0, xvec, vertical_coordinate)
			data1=data1-data0
			vmin=-vanom  ; vmax=vanom


		plt.subplot(3,1,n+1)
		plot_data_field(data1, x1, z1, '', vmin, vmax, rotated=False, colorbar=True, cmap='jet')
		
		#For plotting purposes
		field=field+'_'+ vertical_coordinate




	plt.tight_layout()


	if save_figure==True:
		#output_file='figures/static_shelf_comparison_' + field + '.png'
		#plt.savefig(output_file,dpi=300,bbox_inches='tight')
		#print 'Saving ' ,output_file
		print 'Saving file not working yet'

	#fig.set_size_inches(9,4.5)
	plt.show()
	print 'Script complete'



if __name__ == '__main__':
	main()
	#sys.exit(main())














