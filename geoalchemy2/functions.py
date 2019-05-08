"""

This module defines the :class:`GenericFunction` class, which is the base for
the implementation of spatial functions in GeoAlchemy.  This module is also
where actual spatial functions are defined. Spatial functions supported by
GeoAlchemy are defined in this module. See :class:`GenericFunction` to know how
to create new spatial functions.

.. note::

    By convention the names of spatial functions are prefixed by ``ST_``.  This
    is to be consistent with PostGIS', which itself is based on the ``SQL-MM``
    standard.

Functions created by subclassing :class:`GenericFunction` can be called
in several ways:

* By using the ``func`` object, which is the SQLAlchemy standard way of calling
  a function. For example, without the ORM::

      select([func.ST_Area(lake_table.c.geom)])

  and with the ORM::

      Session.query(func.ST_Area(Lake.geom))

* By applying the function to a geometry column. For example, without the
  ORM::

      select([lake_table.c.geom.ST_Area()])

  and with the ORM::

      Session.query(Lake.geom.ST_Area())

* By applying the function to a :class:`geoalchemy2.elements.WKBElement`
  object (:class:`geoalchemy2.elements.WKBElement` is the type into
  which GeoAlchemy converts geometry values read from the database), or
  to a :class:`geoalchemy2.elements.WKTElement` object. For example,
  without the ORM::

      conn.scalar(lake['geom'].ST_Area())

  and with the ORM::

      session.scalar(lake.geom.ST_Area())

Reference
---------

"""

from sqlalchemy.sql import functions
from sqlalchemy.ext.compiler import compiles

from . import types


class GenericFunction(functions.GenericFunction):
    """
    The base class for GeoAlchemy functions.

    This class inherits from ``sqlalchemy.sql.functions.GenericFunction``, so
    functions defined by subclassing this class can be given a fixed return
    type. For example, functions like :class:`ST_Buffer` and
    :class:`ST_Envelope` have their ``type`` attributes set to
    :class:`geoalchemy2.types.Geometry`.

    This class allows constructs like ``Lake.geom.ST_Buffer(2)``. In that
    case the ``Function`` instance is bound to an expression (``Lake.geom``
    here), and that expression is passed to the function when the function
    is actually called.

    If you need to use a function that GeoAlchemy does not provide you will
    certainly want to subclass this class. For example, if you need the
    ``ST_TransScale`` spatial function, which isn't (currently) natively
    supported by GeoAlchemy, you will write this::

        from geoalchemy2 import Geometry
        from geoalchemy2.functions import GenericFunction

        class ST_TransScale(GenericFunction):
            name = 'ST_TransScale'
            type = Geometry
    """

    _register = False

    def __init__(self, *args, **kwargs):
        expr = kwargs.pop('expr', None)
        if expr is not None:
            args = (expr,) + args
        functions.GenericFunction.__init__(self, *args, **kwargs)


# Functions are classified as in the PostGIS doc.
# <http://www.postgis.org/documentation/manual-svn/reference.html>


_FUNCTIONS = [
    #
    # Geometry Accessors
    #

    ('ST_Boundary', types.Geometry,
     'Returns the closure of the combinatorial boundary of this Geometry.'),

    ('ST_BoundingDiagonal', types.Geometry,
     'Returns the diagonal of the supplied geometry\'s bounding box.'),

    ('ST_EndPoint', types.Geometry,
     'Returns the last point of a ``LINESTRING`` or ``CIRCULARLINESTRING`` '
     'geometry as a ``POINT``.'),

    ('ST_Envelope', types.Geometry,
     'Returns a geometry representing the double precision (float8) bounding'
     'box of the supplied geometry.'),

    ('ST_GeometryN', types.Geometry,
     'Return the 1-based Nth geometry if the geometry is a '
     '``GEOMETRYCOLLECTION``, ``(MULTI)POINT``, ``(MULTI)LINESTRING``, '
     '``MULTICURVE`` or ``(MULTI)POLYGON``, ``POLYHEDRALSURFACE`` Otherwise, '
     'return ``None``.'),

    ('ST_GeometryType', None,
     'Return the geometry type of the ``ST_Geometry`` value.'),

    ('ST_InteriorRingN', types.Geometry,
     'Return the Nth interior linestring ring of the polygon geometry. Return '
     '``NULL`` if the geometry is not a polygon or the given N is out of '
     'range.'),

    ('ST_IsValid', None,
     'Returns ``True`` if the ``ST_Geometry`` is well formed.'),

    ('ST_NPoints', None,
     'Return the number of points (vertices) in a geometry.'),

    ('ST_PatchN', types.Geometry,
     'Return the 1-based Nth geometry (face) if the geometry is a '
     '``POLYHEDRALSURFACE``, ``POLYHEDRALSURFACEM``. Otherwise, return '
     '``NULL``.'),

    ('ST_PointN', types.Geometry,
     'Return the Nth point in the first LineString or circular LineString in '
     'the geometry. Negative values are counted backwards from the end of the '
     'LineString. Returns ``NULL`` if there is no linestring in the geometry.'
     ),

    ('ST_Points', types.Geometry,
     'Returns a MultiPoint containing all of the coordinates of a geometry.'),

    ('ST_SRID', None,
     'Returns the spatial reference identifier for the ``ST_Geometry`` as '
     'defined in ``spatial_ref_sys`` table.'),

    ('ST_StartPoint', types.Geometry,
     'Returns the first point of a ``LINESTRING`` geometry as a ``POINT``.'),

    ('ST_X', None,
     'Return the X coordinate of the point, or ``None`` if not available. '
     'Input must be a point.'),

    ('ST_Y', None,
     'Return the Y coordinate of the point, or ``None`` if not available. '
     'Input must be a point.'),

    ('ST_Z', None,
     'Return the Z coordinate of the point, or ``None`` if not available. '
     'Input must be a point.'),

    #
    # Geometry Editors
    #

    ('ST_AddPoint', types.Geometry,
     'Add a point to a LineString.'),

    ('ST_Affine', types.Geometry,
     'Apply a 3d affine transformation to a geometry.'),

    ('ST_CollectionExtract', types.Geometry,
     'Given a (multi)geometry, return a (multi)geometry consisting only of '
     'elements of the specified type.'),

    ('ST_CollectionHomogenize', types.Geometry,
     'Given a geometry collection, return the "simplest" representation of '
     'the contents.'),

    ('ST_ExteriorRing', types.Geometry,
     'Returns a line string representing the exterior ring of the ``POLYGON`` '
     'geometry. Return ``NULL`` if the geometry is not a polygon. Will not '
     'work with ``MULTIPOLYGON``.'),

    ('ST_Force2D', types.Geometry,
     'Force the geometries into a "2-dimensional mode".'),

    ('ST_Force3D', types.Geometry,
     ('Force the geometries into XYZ mode. This is an alias for ``ST_Force3DZ``.',
      'ST_Force_3D')),

    ('ST_Force3DM', types.Geometry,
     ('Force the geometries into XYM mode.', 'ST_Force_3DM')),

    ('ST_Force3DZ', types.Geometry,
     ('Force the geometries into XYZ mode.', 'ST_Force_3DZ')),

    ('ST_Force4D', types.Geometry,
     ('Force the geometries into XYZM mode.', 'ST_Force_4D')),

    ('ST_ForceCollection', types.Geometry,
     ('Convert the geometry into a ``GEOMETRYCOLLECTION``.',
      'ST_Force_Collection')),

    ('ST_ForceCurve', types.Geometry,
     'Upcast a geometry into its curved type, if applicable.'),

    ('ST_ForcePolygonCCW', types.Geometry,
     'Orients all exterior rings counter-clockwise and all interior rings '
     'clockwise.'),

    ('ST_ForcePolygonCW', types.Geometry,
     'Orients all exterior rings clockwise and all interior rings '
     'counter-clockwise.'),

    ('ST_ForceRHR', types.Geometry,
     'Force the orientation of the vertices in a polygon to follow the '
     'Right-Hand-Rule.'),

    ('ST_ForceSFS', types.Geometry,
     'Force the geometries to use SFS 1.1 geometry types only.'),

    ('ST_M', None,
     'Return the M coordinate of the point, or ``NULL`` if not available. '
     'Input must be a point.'),

    ('ST_Multi', types.Geometry,
     'Return the geometry as a ``MULTI*`` geometry.'),

    ('ST_Normalize', types.Geometry,
     'Return the geometry in its canonical form.'),

    ('ST_QuantizeCoordinates', types.Geometry,
     'Sets least significant bits of coordinates to zero.'),

    ('ST_RemovePoint', types.Geometry,
     'Remove point from a linestring.'),

    ('ST_Reverse', types.Geometry,
     'Return the geometry with vertex order reversed.'),

    ('ST_Rotate', types.Geometry,
     'Rotate a geometry rotRadians counter-clockwise about an origin.'),

    ('ST_RotateX', types.Geometry,
     'Rotate a geometry rotRadians about the X axis.'),

    ('ST_RotateY', types.Geometry,
     'Rotate a geometry rotRadians about the Y axis.'),

    ('ST_RotateZ', types.Geometry,
     'Rotate a geometry rotRadians about the Z axis.'),

    ('ST_Scale', types.Geometry,
     'Scale a geometry by given factors.'),

    ('ST_Segmentize', types.Geometry,
     'Return a modified geometry/geography having no segment longer than the '
     'given distance.'),

    ('ST_SetPoint', types.Geometry,
     'Replace point of a linestring with a given point.'),

    ('ST_SetSRID', types.Geometry,
     'Set the SRID on a geometry to a particular integer value.'),

    ('ST_Snap', types.Geometry,
     'Snap segments and vertices of input geometry to vertices of a reference '
     'geometry.'),

    ('ST_SnapToGrid', types.Geometry,
     'Snap all points of the input geometry to a regular grid.'),

    ('ST_Transform', types.Geometry,
     'Return a new geometry with its coordinates transformed to the SRID '
     'referenced by the integer parameter.'),

    ('ST_Translate', types.Geometry,
     'Translate a geometry by given offsets.'),

    ('ST_TransScale', types.Geometry,
     'Translate a geometry by given factors and offsets.'),

    #
    # Geometry Outputs
    #

    ('ST_AsBinary', None,
     'Return the Well-Known Binary (WKB) representation of the geometry/'
     'geography without SRID meta data.'),

    ('ST_AsEWKB', None,
     'Return the Well-Known Binary (WKB) representation of the geometry/'
     'geography with SRID meta data.'),

    ('ST_AsTWKB', None,
     'Returns the geometry as TWKB, aka "Tiny Well-Known Binary"'),

    ('ST_AsGeoJSON', None, 'Return the geometry as a GeoJSON element.'),

    ('ST_AsGML', None, 'Return the geometry as a GML version 2 or 3 element.'),

    ('ST_AsKML', None,
     'Return the geometry as a KML element. Several variants. Default '
     'version=2, default precision=15'),

    ('ST_AsSVG', None,
     'Returns a Geometry in SVG path data given a geometry or geography '
     'object.'),

    ('ST_AsText', None,
     'Return the Well-Known Text (WKT) representation of the geometry/'
     'geography without SRID metadata.'),

    ('ST_AsEWKT', None,
     'Return the Well-Known Text (WKT) representation of the geometry/'
     'geography with SRID metadata.'),

    #
    # Spatial Relationships and Measurements
    #

    ('ST_Area', None,
     'Returns the area of the surface if it is a polygon or multi-polygon. '
     'For ``geometry`` type area is in SRID units. For ``geography`` area is '
     'in square meters.'),

    ('ST_Azimuth', None,
     'Returns the angle in radians from the horizontal of the '
     'vector defined by pointA and pointB. Angle is computed clockwise from '
     'down-to-up: on the clock: 12=0; 3=PI/2; 6=PI; 9=3PI/2.'),

    ('ST_Centroid', types.Geometry,
     'Returns the geometric center of a geometry.'),

    ('ST_Contains', None,
     'Returns ``True`` if and only if no points of B lie in the exterior of '
     'A, and at least one point of the interior of B lies in the interior '
     'of A.'),

    ('ST_ContainsProperly', None,
     'Returns ``True`` if B intersects the interior of A but not the boundary '
     '(or exterior). A does not contain properly itself, but does contain '
     'itself.'),

    ('ST_Covers', None,
     'Returns ``True`` if no point in Geometry B is outside Geometry A'),

    ('ST_CoveredBy', None,
     'Returns ``True`` if no point in Geometry/Geography A is outside Geometry'
     '/Geography B'),

    ('ST_Crosses', None,
     'Returns ``True`` if the supplied geometries have some, but not all, '
     'interior points in common.'),

    ('ST_Disjoint', None,
     'Returns ``True`` if the Geometries do not "spatially intersect" - if '
     'they do not share any space together.'),

    ('ST_Distance', None,
     'For geometry type Returns the 2-dimensional cartesian minimum distance '
     '(based on spatial ref) between two geometries in projected units. For '
     'geography type defaults to return spheroidal minimum distance between '
     'two geographies in meters.'),

    ('ST_Distance_Sphere', None,
     'Returns minimum distance in meters between two lon/lat geometries. Uses '
     'a spherical earth and radius of 6370986 meters. Faster than '
     '``ST_Distance_Spheroid``, but less accurate. PostGIS versions '
     'prior to 1.5 only implemented for points.'),

    ('ST_DFullyWithin', None,
     'Returns ``True`` if all of the geometries are within the specified '
     'distance of one another'),

    ('ST_DWithin', None,
     'Returns ``True`` if the geometries are within the specified distance of '
     'one another. For geometry units are in those of spatial reference and '
     'for geography units are in meters and measurement is defaulted to '
     '``use_spheroid=True`` (measure around spheroid), for faster check, '
     '``use_spheroid=False`` to measure along sphere.'),

    ('ST_Equals', None,
     'Returns ``True`` if the given geometries represent the same geometry. '
     'Directionality is ignored.'),

    ('ST_Intersects', None,
     'Returns ``True`` if the Geometries/Geography "spatially intersect in '
     '2D" - (share any portion of space) and ``False`` if they don\'t (they '
     'are Disjoint). For geography -- tolerance is 0.00001 meters (so any '
     'points that close are considered to intersect)'),

    ('ST_Length', None,
     'Returns the 2d length of the geometry if it is a linestring or '
     'multilinestring. geometry are in units of spatial reference and '
     'geography are in meters (default spheroid)'),

    ('ST_LineLocatePoint', None,
     'Returns a float between 0 and 1 representing the location of the '
     'closest point on LineString to the given Point, as a fraction of '
     'total 2d line length.'),

    ('ST_OrderingEquals', None,
     'Returns ``True`` if the given geometries represent the same geometry '
     'and points are in the same directional order.'),

    ('ST_Overlaps', None,
     'Returns ``True`` if the Geometries share space, are of the same '
     'dimension, but are not completely contained by each other.'),

    ('ST_Perimeter', None,
     'Return the length measurement of the boundary of an ST_Surface or '
     'ST_MultiSurface geometry or geography. (Polygon, Multipolygon). '
     'geometry measurement is in units of spatial reference and geography is '
     'in meters.'),

    ('ST_Project', types.Geography,
     'Returns a ``POINT`` projected from a start point using a distance in '
     'meters and bearing (azimuth) in radians.'),

    ('ST_Relate', None,
     'Returns ``True`` if this Geometry is spatially related to '
     'anotherGeometry, by testing for intersections between the Interior, '
     'Boundary and Exterior of the two geometries as specified by the values '
     'in the intersectionMatrixPattern. If no intersectionMatrixPattern is '
     'passed in, then returns the maximum intersectionMatrixPattern that '
     'relates the 2 geometries.'),

    ('ST_Touches', None,
     'Returns ``True`` if the geometries have at least one point in common, '
     'but their interiors do not intersect.'),

    ('ST_Within', None,
     'Returns ``True`` if the geometry A is completely inside geometry B'),

    #
    # Geometry Processing
    #

    ('ST_Buffer', types.Geometry,
     'For geometry: Returns a geometry that represents all points whose '
     'distance from this Geometry is less than or equal to distance. '
     'Calculations are in the Spatial Reference System of this Geometry.\n\n'
     'For geography: Uses a planar transform wrapper. Introduced in 1.5 '
     'support for different end cap and mitre settings to control shape.'),

    ('ST_Difference', types.Geometry,
     'Returns a geometry that represents that part of geometry A that does '
     'not intersect with geometry B.'),

    ('ST_Dump', types.GeometryDump,
     'Returns a set of geometry_dump (geom,path) rows, that make up a '
     'geometry g1.'),

    ('ST_DumpPoints', types.GeometryDump,
     'Returns a set of geometry_dump (geom,path) rows of all points that '
     'make up a geometry.'),

    ('ST_Intersection', types.Geometry,
     'Returns a geometry that represents the shared portion of geomA and '
     'geomB. The geography implementation does a transform to geometry to do '
     'the intersection and then transform back to WGS84.'),

    ('ST_LineMerge', types.Geometry,
     'Returns a (set of) LineString(s) formed by sewing together the '
     'constituent line work of a MULTILINESTRING.'),

    ('ST_LineSubstring', types.Geometry,
     'Return a linestring being a substring of the input one starting and '
     'ending at the given fractions of total 2d length. Second and third '
     'arguments are float8 values between 0 and 1. This only works with '
     'LINESTRINGs. To use with contiguous MULTILINESTRINGs use in '
     'conjunction with ST_LineMerge.'
     ''
     'If \'start\' and \'end\' have the same value this is equivalent '
     'to ST_LineInterpolatePoint.'),

    ('ST_Simplify', types.Geometry,
     'Returns a "simplified" version of the given geometry using the '
     'Douglas-Peucker algorithm.'),

    ('ST_Union', types.Geometry,
     'Returns a geometry that represents the point set union of the '
     'Geometries.'),

    #
    # Raster Constructors
    #

    ('ST_GeomFromText', types.Geometry,
     'Constructs a PostGIS ST_Geometry object from the OGC Well-Known text '
     'representation.'),

    ('ST_GeomFromEWKT', types.Geometry,
     'Constructs a PostGIS ST_Geometry object from the OGC Extended Well-Known '
     'text (EWKT) representation.'),

    ('ST_GeomFromEWKB', types.Geometry,
     'Constructs a PostGIS ST_Geometry object from the OGC Extended Well-Known '
     'binary (EWKB) representation.'),

    ('ST_GeogFromText', types.Geography,
     'Returns a geography object from the well-known text or extended well-known '
     'representation.'),

    ('ST_AsRaster', types.Raster,
     ('Converts a PostGIS geometry to a PostGIS raster.', 'RT_ST_AsRaster')),

    #
    # Raster Accessors
    #

    ('ST_Height', None,
     ('Returns the height of the raster in pixels.', 'RT_ST_Height')),

    ('ST_Width', None,
     ('Returns the width of the raster in pixels.', 'RT_ST_Width')),

    #
    # Raster Pixel Accessors and Setters
    #

    ('ST_Value', None,
     ('Returns the value of a given band in a given columnx, rowy pixel or at '
      'a particular geometric point. Band numbers start at 1 and assumed to '
      'be 1 if not specified. If ``exclude_nodata_value`` is set to '
      '``false``, then all pixels include nodata pixels are considered to '
      'intersect and return value. If ``exclude_nodata_value`` is not passed '
      'in then reads it from metadata of raster.', 'RT_ST_Value')),
]

# Iterate through _FUNCTION and create GenericFunction classes dynamically
for name, type_, doc in _FUNCTIONS:
    attributes = {'name': name}
    docs = []

    if isinstance(doc, tuple):
        docs.append(doc[0])
        docs.append('see http://postgis.net/docs/{0}.html'.format(doc[1]))
    elif doc is not None:
        docs.append(doc)
        docs.append('see http://postgis.net/docs/{0}.html'.format(name))

    if type_ is not None:
        attributes['type'] = type_

        type_str = '{0}.{1}'.format(type_.__module__, type_.__name__)
        docs.append('Return type: :class:`{0}`.'.format(type_str))

    if len(docs) != 0:
        attributes['__doc__'] = '\n\n'.join(docs)

    globals()[name] = type(name, (GenericFunction,), attributes)


#
# Define compiled versions for functions in SpatiaLite whose names don't have
# the ST_ prefix.
#


_SQLITE_FUNCTIONS = {
    "ST_GeomFromEWKT": "GeomFromEWKT",
    "ST_GeomFromEWKB": "GeomFromEWKB",
    "ST_AsBinary": "AsBinary",
    "ST_AsEWKB": "AsEWKB",
    "ST_AsGeoJSON": "AsGeoJSON",
}


def _compiles(cls, fn):
    def _compile(element, compiler, **kw):
        return "{}({})".format(fn, compiler.process(element.clauses, **kw))
    compiles(globals()[cls], "sqlite")(_compile)


for cls, fn in _SQLITE_FUNCTIONS.items():
    _compiles(cls, fn)
