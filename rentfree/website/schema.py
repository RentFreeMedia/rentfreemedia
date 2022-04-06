SCHEMA_ORG_TYPES = (
    ('Organization', 'Organization > *'),
    ('Corporation', 'Organization > Corporation'),
    ('LocalBusiness', 'Organization > LocalBusiness'),
    ('EntertainmentBusiness', 'Organization > LocalBusiness > EntertainmentBusiness'),
    ('AdultEntertainment', 'Organization > LocalBusiness > EntertainmentBusiness > AdultEntertainment'),
    ('RadioStation', 'Organization > LocalBusiness > RadioStation'),
    ('NGO', 'Organization > NGO'),
    ('PerformingGroup', 'Organization > PerformingGroup'),
    ('DanceGroup', 'Organization > PerformingGroup > DanceGroup'),
    ('MusicGroup', 'Organization > PerformingGroup > MusicGroup'),
    ('TheaterGroup', 'Organization > PerformingGroup > TheaterGroup'),
    ('SportsOrganization', 'Organization > SportsOrganization'),
    ('SportsTeam', 'Organization > SportsOrganization > SportsTeam')
)

SCHEMA_CONTENT_CHOICES = (
    ('Article', 'Thing > CreativeWork > Article - CreativeWorkSeries'),
    ('Episode', 'Thing > CreativeWork > Episode - PodcastEpisode')
)
