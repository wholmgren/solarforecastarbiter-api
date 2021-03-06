from marshmallow import validate


from sfa_api import spec, ma


VARIABLES = ['ghi', 'dni', 'dhi', 'temp', 'wspd',
             'poa', 'ac_power', 'dc_power']
VARIABLE_FIELD = variable = ma.String(
        title='Variable',
        description="The variable being forecast",
        required=True,
        validate=validate.OneOf(VARIABLES))
EXTRA_PARAMETERS_FIELD = ma.String(
        title='Extra Parameters',
        description='Additional user specified parameters.')


# Sites
@spec.define_schema('ModelingParameters')
class ModelingParameters(ma.Schema):
    ac_power = ma.Float(
        title="AC Power",
        description="Nameplate AC power rating.")
    dc_power = ma.Float(
        title="DC Power",
        description="Nameplate DC power rating.")
    temperature_coefficient = ma.String(
        title="Temperature Coefficient",
        description=("The temperature coefficient of DC power in units of "
                     "1/C. Typically -0.002 to -0.005 per degree C."))
    tracking_type = ma.String(
        title="Tracking Type",
        description=("Type of tracking system, i.e. fixed, single axis, two "
                     "axis."),
        validate=validate.OneOf(['fixed', 'single_axis']))
    # fixed tilt systems
    surface_tilt = ma.Float(
        title="Surface Tilt",
        description="Tilt from horizontal of a fixed tilt system, degrees.")
    surface_azimuth = ma.Float(
        title="Surface Azimuth",
        description="Azimuth angle of a fixed tilt system, degrees.")
    # single axis tracker
    axis_tilt = ma.Float(
        title="Axis tilt",
        description="Tilt from horizontal of the tracker axis, degrees.")
    axis_azimuth = ma.Float(
        title="Axis azimuth",
        description="Azimuth angle of the tracker axis, degrees.")
    ground_coverage_ratio = ma.Float(
        title="Ground coverage ratio",
        description=("Ratio of total width of modules on a tracker to the "
                     "distance between tracker axes. For example, for "
                     "trackers each with two modules of 1m width each, and "
                     "a spacing between tracker axes of 7m, the ground "
                     "coverage ratio is 0.286(=2/7)."))
    backtrack = ma.Boolean(
        title="Backtrack",
        description=("True/False indicator of if a tracking system uses "
                     "backtracking."))
    max_rotation_angle = ma.Float(
        title="Maximum Rotation Angle",
        description=("Maximum rotation from horizontal of a single axis "
                     "tracker, degrees."))


@spec.define_schema('SiteDefinition')
class SiteSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True
    name = ma.String(
        title='Name',
        description="Name of the Site",
        required=True)
    latitude = ma.Float(
        title='Latitude',
        description="Latitude in degrees North",
        required=True)
    longitude = ma.Float(
        title='Longitude',
        description="Longitude in degrees East of the Prime Meridian",
        required=True)
    elevation = ma.Float(
        title='Elevation',
        description="Elevation in meters",
        required=True)
    timezone = ma.String(
        title="Timezone",
        description="IANA Timezone",
        required=True)
    modeling_parameters = ma.Nested(ModelingParameters)
    extra_parameters = EXTRA_PARAMETERS_FIELD


@spec.define_schema('SiteMetadata')
class SiteResponseSchema(SiteSchema):
    site_id = ma.UUID(required=True)
    provider = ma.String()


# Observations
@spec.define_schema('ObservationValue')
class ObservationValueSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True
    timestamp = ma.DateTime(
        title="Timestamp",
        description="ISO 8601 Datetime")
    value = ma.Float(
        description="Value of the measurement")
    quality_flag = ma.Integer(
        description="A flag indicating data quality.",
        default=0, missing=False)


@spec.define_schema('ObservationDefinition')
class ObservationPostSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True
    variable = VARIABLE_FIELD
    site_id = ma.UUID(
        title='Site ID',
        description="UUID the assocaiated site",
        required=True)
    name = ma.String(
        title='Name',
        description='Human friendly name for the observation',
        required=True)
    interval_label = ma.String(
        title='Interval Label',
        description=('For data that represents intervals, indicates if a time '
                     'labels the beginning or ending of the interval. N/A for '
                     'instantaneous data'),
        validate=validate.OneOf(['start', 'end']))
    uncertainty = ma.Float(
        title='Uncertainty',
        description='A measure of the uncertainty of the observation values.')
    extra_parameters = EXTRA_PARAMETERS_FIELD


@spec.define_schema('ObservationMetadata')
class ObservationSchema(ObservationPostSchema):
    class Meta:
        strict = True
        ordered = True
    site = ma.Nested(SiteSchema)
    obs_id = ma.UUID()
    provider = ma.String()


@spec.define_schema('ObservationLinks')
class ObservationLinksSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True
    obs_id = ma.UUID()
    _links = ma.Hyperlinks({
        'metadata': ma.AbsoluteURLFor('observations.metadata',
                                      obs_id='<obs_id>'),
        'values': ma.AbsoluteURLFor('observations.values',
                                    obs_id='<obs_id>')
    })


# Forecasts
@spec.define_schema('ForecastValue')
class ForecastValueSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True
    timestamp = ma.DateTime(
        title="Timestamp",
        description="ISO 8601 Datetime")
    value = ma.Float(
        title="Value",
        description="Value of the forecast variable.")
    quality_flag = ma.Integer(
        title="Questionable",
        description="A flag indicating data quality.",
        default=0, missing=False)


@spec.define_schema('ForecastDefinition')
class ForecastPostSchema(ma.Schema):
    class Meta:
        strict = True
        ordered = True
    site_id = ma.UUID(
        name="Site ID",
        description="UUID of the associated site",
        required=True)
    name = ma.String(
        title='Name',
        description="Human friendly name for forecast",
        required=True)
    variable = VARIABLE_FIELD
    issue_time_of_day = ma.String(
        title='Issue Time of Day',
        required=True,
        description=('The time of day that a forecast run is issued, '
                     'e.g. 00:30. For forecast runs issued multiple '
                     'times within one day (e.g. hourly), this specifies '
                     'the first issue time of day. Additional issue times '
                     'are uniquely determined by the first issue time and '
                     'the run length & issue frequency attribute.'))
    lead_time_to_start = ma.String(
        title='Lead time to start',
        description="Lead time to start of forecast",
        required=True)

    interval_label = ma.String(
        title='Interval Label',
        description=('For data that represents intervals, indicates if a time '
                     'labels the beginning or ending of the interval. N/A for '
                     'instantaneous data'),
        validate=validate.OneOf(['start', 'end']))
    duration = ma.String(
        title='Duration',
        description="Interval duration",
        required=True
    )
    intervals = ma.Integer(
        title='Intervals',
        description="Intervals per submission",
        required=True
    )
    issue_frequency = ma.String(
        title='Issue Frequency',
        description="Forecast issue frequency",
        required=True,
    )
    value_type = ma.String(
        title='Value Type',
        description="Value type (e.g. mean, max, 95th percentile, instantaneous)",  # NOQA
    )
    extra_parameters = EXTRA_PARAMETERS_FIELD


@spec.define_schema('ForecastMetadata')
class ForecastSchema(ForecastPostSchema):
    site = ma.Nested(SiteSchema)
    forecast_id = ma.UUID()
    provider = ma.String()


@spec.define_schema('ForecastLinks')
class ForecastLinksSchema(ma.Schema):
    class Meta:
        string = True
        ordered = True
    forecast_id = ma.UUID()
    _links = ma.Hyperlinks({
        'metadata': ma.AbsoluteURLFor('forecasts.metadata',
                                      forecast_id='<forecast_id>'),
        'values': ma.AbsoluteURLFor('forecasts.values',
                                    forecast_id='<forecast_id>')
    })
