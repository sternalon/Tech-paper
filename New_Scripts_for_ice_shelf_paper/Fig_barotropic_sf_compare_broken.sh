cd ../
./snapshots.py -extension=ocean_month.nc -plot_horizontal_field=True -use_ALE=False  -time_ind1=-1 -time_ind2=-1 -time_ind3=99 -cmap=jet -field=barotropic_sf -vmin=0 -vmax=9.0 -vanom=7000 -use_days_title=False -mask_using_bergs=False -dir_slice_num=1 -colorbar_units='(m/yr)' -use_Mixed_Melt=False -dashed_num=12 -plot_second_colorbar=False -second_colorbar_units='(m)' -use_Revision=False -simulation=Wind_Broken_Compare -use_simulations_with_wind=True -plot_anomaly=True -ylim_min=130.0 -ylim_max=480.0 -mask_out_ocean=False -save_figure=True
