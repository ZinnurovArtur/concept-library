'''
    --------------------------------------------------------------------------
    URLs
    URL routing for the API.
    --------------------------------------------------------------------------
'''
from django.conf.urls import url, include
from rest_framework import routers
#from . import views
#from cll import settings
from django.conf import settings
from .views import (View, Concept, WorkingSet, Phenotype, DataSource)

from clinicalcode.views import View as cc_view
 
'''
Use the default REST API router to access the API details explicitly.
These paths will appear as links on the API page.
'''
router = routers.DefaultRouter()
router.register('concepts-live', Concept.ConceptViewSet)
router.register('codes', Concept.CodeViewSet)
router.register('tags', View.TagViewSet, basename='tags')
router.register('datasources2', View.DataSourceViewSet)


'''
Paths which are available as REST API URLs. The router URLs listed above can
be included via an include().
'''
urlpatterns = [
    url(r'^$', cc_view.customRoot, name='root'),    
    url(r'^', include(router.urls)),
      
    #----------------------------------------------------------  
    # ---  concepts  ------------------------------------------
    #----------------------------------------------------------    
      
    url(r'^concepts/C(?P<pk>\d+)/export/codes/$',
        Concept.export_concept_codes,
        name='api_export_concept_codes'),
    
    url(r'^concepts/C(?P<pk>\d+)/version/(?P<concept_history_id>\d+)/export/codes/$',
        Concept.export_concept_codes_byVersionID,
        name='api_export_concept_codes_byVersionID'),
    
    url(r'^public/concepts/C(?P<pk>\d+)/version/(?P<concept_history_id>\d+)/export/codes/$',
        Concept.export_published_concept_codes,
        name='api_export_published_concept_codes'),
    
    #===============================================
    # only superuser - under testing
    url(r'^childconcepts/C(?P<pk>\d+)/$',
        Concept.child_concepts,
        name='api_child_concepts'),
    
    # only superuser - under testing
    url(r'^parentconcepts/C(?P<pk>\d+)/$',
        Concept.parent_concepts,
        name='api_parent_concepts'),
       
    # concepts_live_and_published  used for internal search for concepts (not useful for external api user)
    url(r'^concept-search/$',
        Concept.concepts_live_and_published,
        name='concepts_live_and_published'),
    
    
    #==== search concepts/published concepts =======
    # search user concepts
    url(r'^concepts/$',
        Concept.user_concepts,
        name='concepts'),
     
    url(r'^concepts/C(?P<pk>\d+)/$',
        Concept.user_concepts,
        name='concept_by_id'),

    # search published concepts
    url(r'^public/concepts/$',
        Concept.published_concepts,
        name='api_published_concepts'),
    
    url(r'^public/concepts/C(?P<pk>\d+)/$',
        Concept.published_concepts,
        name='api_published_concept_by_id'),
    #================================================


    # get concept detail
    # if only concept_id is provided, get the latest version
    url(r'^concepts/C(?P<pk>\d+)/detail/$',
        Concept.concept_detail,
        name='api_concept_detail'),
    url(r'^public/concepts/C(?P<pk>\d+)/detail/$',
        Concept.concept_detail_PUBLIC,
        name='api_concept_detail_public'),
                  
    # get specific version
    url(r'^concepts/C(?P<pk>\d+)/version/(?P<concept_history_id>\d+)/detail/$',
        Concept.concept_detail,
        name='api_concept_detail_version'),
    url(r'^public/concepts/C(?P<pk>\d+)/version/(?P<concept_history_id>\d+)/detail/$',
        Concept.concept_detail_PUBLIC,
        name='api_concept_detail_version_public'),
    
    # show versions
    url(r'^concepts/C(?P<pk>\d+)/get-versions/$',
        Concept.concept_detail, {'get_versions_only':'1'},
        name='get_concept_versions'),
    url(r'^public/concepts/C(?P<pk>\d+)/get-versions/$',
        Concept.concept_detail_PUBLIC, {'get_versions_only':'1'},
        name='get_concept_versions_public'),
    
    
    
    
    
    #----------------------------------------------------------  
    # ---  working sets  --------------------------------------      
    #----------------------------------------------------------  
    
    url(r'^workingsets/WS(?P<pk>\d+)/export/codes/$',
        WorkingSet.export_workingset_codes,
        name='api_export_workingset_codes'),

    url(r'^workingsets/WS(?P<pk>\d+)/version/(?P<workingset_history_id>\d+)/export/codes/$',
        WorkingSet.export_workingset_codes_byVersionID,
        name='api_export_workingset_codes_byVersionID'),    
        
    
    
    # search my working sets
    url(r'^workingsets/$',
        WorkingSet.workingsets,
        name='workingsets'),
        
    url(r'^workingsets/WS(?P<pk>\d+)/$',
        WorkingSet.workingsets,
        name='workingset_by_id'),
    
    # my working set detail
    # if only workingset_id is provided, get the latest version
    url(r'^workingsets/WS(?P<pk>\d+)/detail/$',
        WorkingSet.workingset_detail,
        name='api_workingset_detail'),
    # get specific version
    url(r'^workingsets/WS(?P<pk>\d+)/version/(?P<workingset_history_id>\d+)/detail/$',
        WorkingSet.workingset_detail,
        name='api_workingset_detail_version'),    
    
    # show versions
    url(r'^workingsets/WS(?P<pk>\d+)/get-versions/$',
            WorkingSet.workingset_detail, {'get_versions_only':'1'},
            name='get_workingset_versions'),    
    
    #----------------------------------------------------------
    # --- phenotypes   ----------------------------------------
    #----------------------------------------------------------  
    
    url(r'^phenotypes/PH(?P<pk>\d+)/version/(?P<phenotype_history_id>\d+)/export/codes/$',
        Phenotype.export_phenotype_codes_byVersionID,
        name='api_export_phenotype_codes_byVersionID'),
    
    url(r'^public/phenotypes/PH(?P<pk>\d+)/version/(?P<phenotype_history_id>\d+)/export/codes/$',
        Phenotype.export_published_phenotype_codes,
        name='api_export_published_phenotype_codes'),

    #==== search concepts/published phenotypes =====
    url(r'^phenotypes/$',
        Phenotype.phenotypes,
        name='phenotypes'),
    url(r'^phenotypes/PH(?P<pk>\d+)/$',
        Phenotype.phenotypes,
        name='phenotype_by_id'),

    # search published phenotypes
    url(r'^public/phenotypes/$',
        Phenotype.published_phenotypes,
        name='api_published_phenotypes'),
    
    url(r'^public/phenotypes/PH(?P<pk>\d+)/$',
        Phenotype.published_phenotypes,
        name='api_published_phenotype_by_id'),       
    #===============================================
    
    # my phenotype detail
    # if only phenotype_id is provided, get the latest version
    url(r'^phenotypes/PH(?P<pk>\d+)/detail/$',
            Phenotype.phenotype_detail,
            name='api_phenotype_detail'),
    url(r'^public/phenotypes/PH(?P<pk>\d+)/detail/$',
            Phenotype.phenotype_detail_PUBLIC,
            name='api_phenotype_detail_public'),
                  
    # get specific version
    url(r'^phenotypes/PH(?P<pk>\d+)/version/(?P<phenotype_history_id>\d+)/detail/$',
        Phenotype.phenotype_detail,
        name='api_phenotype_detail_version'),
    url(r'^public/phenotypes/PH(?P<pk>\d+)/version/(?P<phenotype_history_id>\d+)/detail/$',
        Phenotype.phenotype_detail_PUBLIC,
        name='api_phenotype_detail_version_public'),
    
    # show versions
    url(r'^phenotypes/PH(?P<pk>\d+)/get-versions/$',
            Phenotype.phenotype_detail, {'get_versions_only':'1'},
            name='get_phenotype_versions'),
    url(r'^public/phenotypes/PH(?P<pk>\d+)/get-versions/$',
            Phenotype.phenotype_detail_PUBLIC, {'get_versions_only':'1'},
            name='get_phenotype_versions_public'),
    
    
    # ---------------------------------------------------------  
    # ---  data sources  --------------------------------------
    #----------------------------------------------------------
    
    #==== search data sources =====
    url(r'^data-sources/$',
        DataSource.data_sources,
        name='data_sources'),
    url(r'^data-sources/(?P<pk>\d+)/$',
        DataSource.data_sources,
        name='data_source_by_id'),    
    
    # public 
    url(r'^public/data-sources/$',
        DataSource.published_data_sources, {'show_published_data_only': True},
        name='data_sources_public'),
    url(r'^public/data-sources/(?P<pk>\d+)/$',
        DataSource.published_data_sources, {'show_published_data_only': True},
        name='data_source_by_id_public'), 
        
        
    # only get live phenotypes 
    url(r'^data-sources/live/$',
        DataSource.data_sources, {'get_live_phenotypes': True},
        name='data_sources_live'),
    url(r'^data-sources/live/(?P<pk>\d+)/$',
        DataSource.data_sources, {'get_live_phenotypes': True},
        name='data_source_live_by_id'),    
    
    # only get live published phenotypes 
    url(r'^public/data-sources/live/$',
        DataSource.published_data_sources, {'get_live_phenotypes': True, 'show_published_data_only': True},
        name='data_sources_live_public'),
    url(r'^public/data-sources/live/(?P<pk>\d+)/$',
        DataSource.published_data_sources, {'get_live_phenotypes': True, 'show_published_data_only': True},
        name='data_source_live_by_id_public'),    
]


#======== Concept/Working set/Phenotye create/update ===================
if not settings.CLL_READ_ONLY:
    urlpatterns += [
        url(r'^api_concept_create/$',
            Concept.api_concept_create,
            name='api_concept_create'),           

        url(r'^api_concept_update/$',
            Concept.api_concept_update,
            name='api_concept_update'),   
                
        
        
        url(r'^api_workingset_create/$',
            WorkingSet.api_workingset_create,
            name='api_workingset_create'),
        
        url(r'^api_workingset_update/$',
            WorkingSet.api_workingset_update,
            name='api_workingset_update'),
        
        
        
        url(r'^api_phenotype_create/$',
            Phenotype.api_phenotype_create,
            name='api_phenotype_create'),
        
        url(r'^api_phenotype_update/$',
            Phenotype.api_phenotype_update,
            name='api_phenotype_update'),
        
        

        url(r'^api_datasource_create/$',
            DataSource.api_datasource_create,
            name='api_datasource_create')
    ]
    
    


