import netCDF4 as netcdf
from dateutil.relativedelta import relativedelta
import numpy as np


def to_relativedelta(tdelta):

    return relativedelta(seconds=int(tdelta.total_seconds()),
                         microseconds=tdelta.microseconds)


def datetime2gradstime(date):

    #Convert datetime to grads time
    str = date.strftime('%HZ%d%b%Y')

    return str


def gradstime2datetime(str):

    #Convert grads time to datetime
    date = datetime.datetime.strptime(str, '%HZ%d%b%Y')

    return date


def Create_HDF_File(dims, file, vars, vars_info, tinitial, tstep, nt):

    nlat = dims['nlat']
    nlon = dims['nlon']
    res = dims['res']
    minlon = dims['minlon']
    minlat = dims['minlat']
    undef = dims['undef']
    t = np.arange(0, nt * tstep, tstep)

    #Prepare the netcdf file
    #Create file
    f = netcdf.Dataset(file, 'w')

    #Define dimensions
    f.createDimension('lon', nlon)
    f.createDimension('lat', nlat)
    f.createDimension('t', len(t))

    #Longitude
    f.createVariable('lon', 'd', ('lon', ))
    f.variables['lon'][:] = np.linspace(minlon, minlon + res * (nlon - 1),
                                        nlon)
    f.variables['lon'].units = 'degrees_east'
    f.variables['lon'].long_name = 'Longitude'
    f.variables['lon'].res = res

    #Latitude
    f.createVariable('lat', 'd', ('lat', ))
    f.variables['lat'][:] = np.linspace(minlat, minlat + res * (nlat - 1),
                                        nlat)
    f.variables['lat'].units = 'degrees_north'
    f.variables['lat'].long_name = 'Latitude'
    f.variables['lat'].res = res

    #Time
    times = f.createVariable('t', 'd', ('t', ))
    f.variables['t'][:] = t
    f.variables['t'].units = 'hours since %04d-%02d-%02d %02d:00:00.0' % (
        tstep, tinitial.year, tinitial.month, tinitial.day, tinitial.hour)
    f.variables['t'].long_name = 'Time'

    #Data
    i = 0
    for var in vars:
        f.createVariable(var, 'f', ('t', 'lat', 'lon'), fill_value=undef)
        f.variables[var].long_name = vars_info[i]
        i = i + 1

    return f


def Create_NETCDF_File(md):

    nlat = md['nlat']
    nlon = md['nlon']
    res = md['res']
    minlon = md['minlon'] + res / 2
    minlat = md['minlat'] + res / 2
    undef = md['undef']
    nt = md['nt']
    tstep = md['tstep']
    tinitial = md['tinitial']
    tinitial_all = md['tinitial_all']
    vars = md['vars']
    if 'vars_info' in md: vars_info = md['vars_info']
    else: vars_info = vars
    file = md['file']

    #Determine the initial it
    it = int((tinitial - tinitial_all).total_seconds() / 3600.0)
    if nt > 0: t = np.arange(it, nt + it)

    #Prepare the netcdf file
    #Create file
    f = netcdf.Dataset(file, 'w')

    #Define dimensions
    f.createDimension('lon', nlon)
    f.createDimension('lat', nlat)
    if nt > 0: f.createDimension('t', None)  #len(t))

    #Longitude
    f.createVariable('lon', 'd', ('lon', ))
    f.variables['lon'][:] = np.linspace(minlon, minlon + res * (nlon - 1),
                                        nlon)
    f.variables['lon'].units = 'degrees_east'
    f.variables['lon'].long_name = 'Longitude'
    f.variables['lon'].res = res

    #Latitude
    f.createVariable('lat', 'd', ('lat', ))
    f.variables['lat'][:] = np.linspace(minlat, minlat + res * (nlat - 1),
                                        nlat)
    f.variables['lat'].units = 'degrees_north'
    f.variables['lat'].long_name = 'Latitude'
    f.variables['lat'].res = res

    #Time
    if nt > 0:
        times = f.createVariable('t', 'd', ('t', ))
        f.variables['t'][:] = t
        f.variables['t'].units = '%s since %04d-%02d-%02d %02d:00:00.0' % (
            'hours', tinitial_all.year, tinitial_all.month, tinitial_all.day,
            tinitial_all.hour)
        f.variables['t'].long_name = 'Time'

    #Data
    i = 0
    for var in vars:
        if nt > 0:
            f.createVariable(var, 'f', ('t', 'lat', 'lon'), fill_value=undef)
        else:
            f.createVariable(var, 'f', ('lat', 'lon'), fill_value=undef)
        f.variables[var].long_name = vars_info[i]
        i = i + 1

    return f


def Update_Control_File(type, idate, dims, nt, tstep, file_template, ctl_file):

    if type == 'nc':
        fp = open(ctl_file, 'w')
        fp.write('dset %s\n' % file_template)
        fp.write('options template\n')
        fp.write('dtype netcdf\n')
        fp.write('tdef t %d linear %s %s\n' %
                 (nt, datetime2gradstime(idate), tstep))
        fp.close()


def Update_Control_File_Binary(type, idate, dims, nt, tstep, file_template,
                               ctl_file, vars):

    if type == 'bin_all':
        fp = open(ctl_file, 'w')
        fp.write('dset %s\n' % file_template)
        fp.write('title %s\n' % file_template)
        fp.write('undef %f\n' % dims['undef'])
        fp.write('xdef %d linear %f %f\n' %
                 (dims['nlon'], dims['minlon'], dims['res']))
        fp.write('ydef %d linear %f %f\n' %
                 (dims['nlat'], dims['minlat'], dims['res']))
        fp.write('zdef 1 levels 0\n')
        fp.write('tdef %d linear %s %s\n' %
                 (nt, datetime2gradstime(idate), tstep))
        fp.write('vars %d\n' % len(vars))
        for var in vars:
            fp.write('%s 0 99 %s\n' % (var, var))
        fp.write('endvars\n')
        fp.close()

    return
