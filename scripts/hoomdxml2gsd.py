#!/usr/bin/python

import argparse
import xml.dom.minidom
import gsd.fl
import gsd.hoomd
import numpy

def read_xml(name):
    snap = gsd.hoomd.Snapshot();

    # parse the XML file
    dom = xml.dom.minidom.parse(open(name, 'r'));
    hoomd_xml = dom.getElementsByTagName('hoomd_xml');
    if len(hoomd_xml) != 1:
        raise RuntimeError("hoomd_xml tag not found in xml file")
    else:
        hoomd_xml = hoomd_xml[0];

    configuration = hoomd_xml.getElementsByTagName('configuration');
    if len(configuration) != 1:
        raise RuntimeError("configuration tag not found in xml file")
    else:
        configuration = configuration[0];

    # determine the number of dimensions
    if configuration.hasAttribute('dimensions'):
        snap.configuration.dimensions = int(configuration.getAttribute('dimensions'));
    else:
        snap.configuration.dimensions = 3;

    # determine the time step
    if configuration.hasAttribute('time_step'):
        snap.configuration.step = int(configuration.getAttribute('time_step'));
    else:
        snap.configuration.step = 3;

    box_config = configuration.getElementsByTagName('box')[0]
    lx = ly = lz = 1;
    xy = xz = yz = 0;
    if box_config.hasAttribute('xy'):
        xy = float(box_config.getAttribute('xy'))
    if box_config.hasAttribute('xz'):
        xz = float(box_config.getAttribute('xz'))
    if box_config.hasAttribute('yz'):
        yz = float(box_config.getAttribute('yz'))
    if box_config.hasAttribute('lx'):
        lx = float(box_config.getAttribute('lx'))
    if box_config.hasAttribute('ly'):
        ly = float(box_config.getAttribute('ly'))
    if box_config.hasAttribute('lz'):
        lz = float(box_config.getAttribute('lz'))

    snap.configuration.box = numpy.array([lx, ly, lz, xy, xz, yz], dtype=numpy.float32);

    # read the position node just to get the number of particles
    # unless there is no dcd file. Then read positions.
    position = configuration.getElementsByTagName('position');
    if len(position) != 1:
        raise RuntimeError("position tag not found in xml file")
    else:
        position = position[0];
    position_text = position.childNodes[0].data
    xyz = position_text.split()
    snap.particles.N = int(len(xyz)/3)

    snap.particles.position = numpy.array(xyz, dtype=numpy.float32);
    snap.particles.position = snap.particles.position.reshape((snap.particles.N,3))

    # parse the particle types
    type_nodes = configuration.getElementsByTagName('type');
    if len(type_nodes) == 1:
        type_text = type_nodes[0].childNodes[0].data;
        type_names = type_text.split();
        if len(type_names) != snap.particles.N:
            raise RuntimeError("wrong number of types found in xml file")
    else:
        raise RuntimeError("type tag not found in xml file")

    # TODO: assign type names to type ids

    # parse the particle masses
    mass_nodes = configuration.getElementsByTagName('mass');
    if len(mass_nodes) == 1:
        mass_text = mass_nodes[0].childNodes[0].data;
        mass_list = mass_text.split();
        if len(mass_list) != snap.particles.N:
            raise RuntimeError("wrong number of masses found in xml file")
        snap.particles.mass = numpy.array(mass_list, dtype=numpy.float32);

    # parse the particle diameters
    diam_nodes = configuration.getElementsByTagName('diameter');
    if len(diam_nodes) == 1:
        diam_text = diam_nodes[0].childNodes[0].data;
        diam_list = diam_text.split();
        if len(diam_list) != snap.particles.N:
            raise RuntimeError("wrong number of diameters found in xml file")
        snap.particles.diameter = numpy.array(diam_list, dtype=numpy.float32);

    # parse the particle charges
    charge_nodes = configuration.getElementsByTagName('charge');
    if len(charge_nodes) == 1:
        charge_text = charge_nodes[0].childNodes[0].data;
        charge_list = charge_text.split();
        if len(charge_list) != snap.particles.N:
            raise RuntimeError("wrong number of charges found in xml file")
        snap.particles.charge = numpy.array(charge_list, dtype=numpy.float32);

    # parse the moments of inertia
    moment_inertia_nodes = configuration.getElementsByTagName('moment_inertia');
    if len(moment_inertia_nodes) == 1:
        moment_inertia_text = moment_inertia_nodes[0].childNodes[0].data;
        moment_inertia_list = moment_inertia_text.split();
        if len(moment_inertia_list) != snap.particles.N*3:
            raise RuntimeError("wrong number of moments found in xml file")

        snap.particles.moment_inertia = numpy.array(moment_inertia_list, dtype=numpy.float32);
        snap.particles.moment_inertia = snap.particles.moment_inertia.reshape((snap.particles.N,3))

    # parse the images
    image_nodes = configuration.getElementsByTagName('image');
    if len(image_nodes) == 1:
        image_text = image_nodes[0].childNodes[0].data;
        image_list = image_text.split();
        if len(image_list) != snap.particles.N*3:
            raise RuntimeError("wrong number of images found in xml file")

        snap.particles.image = numpy.array(image_list, dtype=numpy.int32);
        snap.particles.image = snap.particles.image.reshape((snap.particles.N,3))

    # parse the velocities
    velocity_nodes = configuration.getElementsByTagName('velocity');
    if len(velocity_nodes) == 1:
        velocity_text = velocity_nodes[0].childNodes[0].data;
        velocity_list = velocity_text.split();
        if len(velocity_list) != snap.particles.N*3:
            raise RuntimeError("wrong number of velocities found in xml file")

        snap.particles.velocity = numpy.array(velocity_list, dtype=numpy.float32);
        snap.particles.velocity = snap.particles.velocity.reshape((snap.particles.N,3))

    # parse the orientations
    orientation_nodes = configuration.getElementsByTagName('orientation');
    if len(orientation_nodes) == 1:
        orientation_text = orientation_nodes[0].childNodes[0].data;
        orientation_list = orientation_text.split();
        if len(orientation_list) != snap.particles.N*4:
            raise RuntimeError("wrong number of orientations found in xml file")

        snap.particles.orientation = numpy.array(orientation_list, dtype=numpy.float32);
        snap.particles.orientation = snap.particles.orientation.reshape((snap.particles.N,4))

    # parse the angular momentum
    angmom_nodes = configuration.getElementsByTagName('angmom');
    if len(angmom_nodes) == 1:
        angmom_text = angmom_nodes[0].childNodes[0].data;
        angmom_list = angmom_text.split();
        if len(angmom_list) != snap.particles.N*4:
            raise RuntimeError("wrong number of angmoms found in xml file")

        snap.particles.angmomg = numpy.array(angmom_list, dtype=numpy.float32);
        snap.particles.angmomg = snap.particles.angmomg.reshape((snap.particles.N,4))

    return snap;

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert HOOMD-blue XML file to GSD.')
    parser.add_argument('input', type=str, nargs=1,
                        help='Input file')
    parser.add_argument('output', type=str, nargs=1,
                        help='Output file')
    args = parser.parse_args()

    print('Reading input file...', flush=True)
    snap = read_xml(args.input[0]);
    print('Writing output file...', flush=True)
    gsd.hoomd.create(args.output[0], snap);