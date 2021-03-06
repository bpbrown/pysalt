.. _saltmosaic:

**********
saltmosaic
**********


Name
====

saltmosaic -- mosaic multiple CCD amplifier images

Usage
=====

saltmosaic images outimages outpref geomfile interp (cleanup) (clobber)
logfile (verbose) (status)

Parameters
==========


*images*
    String. List of input images including, if necessary, absolute or
    relative paths to the data. Data can be provided as a comma-separated
    list, or a string with a wildcard (e.g. 'images=S20061210*.fits'), or
    a foreign file containing an ascii list of image filenames. For ascii
    list option, the filename containing the list must be provided
    preceded by a '@' character, e.g. 'images=@listoffiles.lis'. Do not
    provide any files that have already been mosaiced.

*outimages*
    String. A list of images. Data can be provided as a comma-separated
    list, or a string with a wildcard (e.g. 'outimages=rS20061210*.fits'),
    or a foreign file containing an ascii list of image filenames. For the
    ascii list option, the filename containing the list must be provided
    preceded by a '@' character, e.g. 'outimages=@listoffiles.lis'. This
    list must be of the same size as the images argument list. If the
    output is intended for a different directory the absolute or relative
    path must be supplied with the file name.
    .e

*outpref*
        String. If the outpref string is non-zero in length and contains
        characters other than a blank space, it will override any value of the
        outimages argument. Output file names will use the name list provided
        in the images argument, but adding a prefix to each output file
        defined by outpref. An absolute or relative directory path can be
        included in the prefix, e.g. 'outpref=/Volumes/data/b'.

*geomfile*
        String. This is the name of an ascii table that contains parameters
        describing the relational focal plane geometry between CCDs of a
        detector array. Working examples are stored in
        /iraf/extern/salt/salticam/data/SALTICAMgeom.dat and
        /iraf/extern/salt/pfis/data/PFISgeom.dat. The table is used both to
        rotate and translate CCD images with respect to each other before
        stitching them together within a single image.  An example of the
        table format follows::

            # PFIS CCD Geometry data
            # Date    gap xshift(1) yshift(1) rot(1) xshift(3) yshift(3) rot(3)
            2004-01-01  90  -14.53   1.84    0.0931    2.35      0.84   -0.0337

        Lines beginning with the character '#' are ignored as comments. The
        date refers to the day after which the geometry is valid, but this is
        currently an unused parameter. 'gap' refers to the idealized distance
        between neighburing CCDs. Note that there are two CCD gaps in the RSS
        mosaic which are not of identical size, but there is only one gap
        parameter in the goemtry file. 'xshift' refers to an additional
        translation performed on the CCD after the gap has been
        introduced. Regardless of the instrument, CCD number 2 is always
        considered the reference CCD. This is the right-most CCD in the
        SALTICAM 2x1 mosiac and the middle CCD in the RSS 3x1 mosaic. The
        reference CCD is neither translated or rotated. All other CCDs are
        translated and rotated relative to the reference CCD. xshift(1) refers
        to the translation in the x-direction of the first CCD and xshift(3)
        refers to the translation in the x-direction of the third CCD. xshift
        is used to create CCD gaps of differing size according to on-sky
        calibration of the CCD geometry. 'yshift' refers to a CCD translation
        in the y-direction.  gap, xshift and yshift are all recorded in raw,
        unbinned pixel units. 'rot' refers to a CCD rotation relative to the
        reference CCD with units of degrees.

*interp*
        
        String. The interpolation scheme used to rebin pixel values during
        translation and rotation. The choices are::

            linear  -- linear function
            nearest -- nearest pixel center
            poly3   -- 3rd order polynomial function
            poly5   -- 5th order polynomial function
            spline3 -- cubic spline function
            sinc    -- sinc function

        'nearest' is the least expensive for CPU processing but the least
        accurate, the 'sinc' function is the most expensive.

*(cleanup)*
        Hidden Boolean. If cleanup='yes', all intermediate files will be deleted
        at the end of the task. The default is cleanup='yes'.

*(clobber)*
        Hidden boolean. If clobber='yes', files contained within the working
        directory will be overwritten by newly created files of the same
        name. The default is clobber='no'.

*logfile*
        String. Name of an ascii file for storing log and error messages
        written by the task. The file may be new, or messages can also be
        appended to a pre-existing file.

*(verbose)*
        Hidden Boolean. If verbose='no', log messages will be suppressed from
        both the terminal and the log file.  Error messages are excluded from
        this rule.

*(status)*
        Hidden Integer. Provided status=0 is passed to saltmosaic, a successful
        run of the task will yield status=0 at completion of the task.  Any
        other value for the status flag at completion indicates failed
        execution.

Description
===========

Raw SALT data is stored in FITS files using separate file extensions
for each amplifier image. Each CCD has two readout amplifiers and each
detector has mulitiple CCDs. Hence a single RSS exposure is stored in
2x3 FITS extensions and single SALTICAM image is stored in 2x2 FITS
extensions.  saltmosaic combines a set of amplifier images, obtained
during the same exposure, into a single mosaiced image, stored in a
single extension of the output FITS file.

The primary extension of the output file is a direct copy of the
primary HDU in the input file. The majority of primary header keywords
are also propagated into the image extensions of the output
file. While this results in repetition of the keywords within the
file, this procedure does improve the efficiency of extracting
mosaiced data into 1- or 0-dimensional form.

Before performing mosaicing tasks, saltmosaic checks each input file
to ascertain that it has not already been mosaiced. The flag is
provided by the PMOSAIC or SMOSAIC keywords written to the primary
extension of output by saltmosaic after a successful mosaic.  If the
number of HDU in the input FITS file are not consistent with the
geometry defined in the CCD geometry file the task will quit.

saltmosaic assumes that the overscan and underscan regions have been
trimmed from the input image using e.g. the saltbias task.

Slot mode data is often stored with multiple exposures contained in a
single file. saltmosaic handles slot mode consistently, i.e. if an
input SALTICAM FITS file contains four exposures (16 image HDUs in
total) then the output file will also contains four exposures (4 image
HDUs in total).

slotmosaic performs its task in three steps:

1. For each CCD in the array, stitch the two amplifers together. This
step produces a temporary FITS file, stored in the working
directory, with one extension for each CCD. If the data was
obtained in slot mode, the number of extensions will be a multiple
of the number of CCDs in the array.

2. Rotate and translate CCD images with respect to the reference CCD
using the data stored in the geometry file 'geomfile'. This step is
performed by the IRAF tool iraf.images.immatch.geotran. geotran
writes further temporary files, one for each rotated and translated
CCD image.  No temporary file is created for the reference CCD
which remains unchanged after this step.

3. For each exposure, stitch the CCDs together to form a single image,
written to a file with the specified output name. This step is
where the CCD gaps are introduced to the data. The output file will
contain a primary extension containing only keywords and an image
extension containing the mosaiced data. Slot mode data will contain
multiple image extensions in the output, one for each exposure in
the input image.

The accuracy and form of pixel interpolation performed by geotran is
governed by the interp argument. interp='nearest' provdes the greatest
speed but the least accuracy.

If cleanup='no' then all temporary files will be deleted from the
disk.

Examples
========

1. To mosaic a sequence of RSS image::

    --> saltmosaic images='/Volumes/data1/bxpP*.fits' outimages=''
    outpref='/Volumes/data2/m' geomfile='PFISgeom.dat'
    interp='linear' cleanup='yes' clobber='yes'
    logfile='salt.log' verbose='yes'

Time and disk requirements
==========================

Raw, unbinned RSS images have sizes exceeding 100 MB each.  On a
linux machine with 2.8 Ghz processor and 2 Gb of RAM, one 2051x2051 image can
be processed in in 1.38 sec.

Bugs and limitations
====================

No distortion correction is performed on the amplifier images before
they are mosaiced. Image distortion has yet to be calibrated or
monitored on the SALT instruments.

Send feedback and bug reports to salthelp@saao.ac.za

See also
========

 :ref:`saltclean` :ref:`iraf.images.immatch.geotran`