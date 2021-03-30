'''
    ---------------------------------------------------------------------------
    API VIEW
    API access to the data to list the various data types (if access is
    permitted) and to access the data structure and components of groups of
    data types.
    ---------------------------------------------------------------------------
'''
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from django.http.response import Http404
from django.db.models import Q

from ..serializers import *

# The models imports have to be done as follows to avoid Eclipse flagging up
# access to the objects list as ambiguous.
from ...models.Concept import Concept
from ...models.Component import Component
from ...models.CodeRegex import CodeRegex
from ...models.CodeList import CodeList
from ...models.Code import Code
from ...models.Tag import Tag
from ...models.ConceptTagMap import ConceptTagMap
from ...models.WorkingSet import WorkingSet
from ...models.WorkingSetTagMap import WorkingSetTagMap
from ...models.CodingSystem import CodingSystem
from ...models.Brand import Brand
from ...models.PublishedConcept import PublishedConcept
from django.contrib.auth.models import User

from ...db_utils import *
from ...viewmodels.js_tree_model import TreeModelManager
#from django.forms.models import model_to_dict
from ...permissions import *

from collections import OrderedDict
from django.core.exceptions import PermissionDenied
import json
from clinicalcode.context_processors import clinicalcode
from collections import OrderedDict as ordr
from ...utils import *
from numpy.distutils.fcompiler import none

from django.core import serializers
from datetime import datetime
# from snippets.models import Snippet
# from snippets.serializers import SnippetSerializer
from django.core.validators import URLValidator
from View import *
from django.views.defaults import permission_denied
from django.db.models.aggregates import Max
from clinicalcode.permissions import get_visible_concepts_live
#from ...permissions import Permissions

#--------------------------------------------------------------------------
'''
    ---------------------------------------------------------------------------
    View sets (see http://www.django-rest-framework.org/api-guide/viewsets).
    ---------------------------------------------------------------------------
'''
# /api/concepts
class ConceptViewSet(viewsets.ReadOnlyModelViewSet): 
    '''
        Get the API output for the list of concepts.
    '''
    queryset = Concept.objects.none()
    serializer_class = ConceptSerializer

    def get_queryset(self):
        '''
            Provide the dataset for the view.
            Restrict this to just those concepts that are visible to the user.
        '''
        queryset = get_visible_concepts_live(self.request.user)
        search = self.request.query_params.get('search', None)
        concept_id_to_exclude = self.request.query_params.get('concept_id_to_exclude')
        if search is not None:
            queryset = queryset.filter(name__icontains=search).exclude(id=concept_id_to_exclude).exclude(is_deleted=True)
        return queryset
    

    def filter_queryset(self, queryset):
        '''
            Override the default filtering.
            By default we get concepts ordered by creation date even if
            we provide sorted data from get_queryset(). We have to sort the
            data here.
        '''
        queryset = super(ConceptViewSet, self).filter_queryset(queryset)
        return queryset.order_by('id')

#--------------------------------------------------------------------------
# /api/concepts_live_and_published
@api_view(['GET']) 
def concepts_live_and_published(request):
    
    search = request.query_params.get('search', "")
    concept_id_to_exclude = utils.get_int_value(request.query_params.get('concept_id_to_exclude', 0), 0)
    
    rows_to_return = get_visible_live_or_published_concept_versions(request
                                                                    , searchByName = search
                                                                    , concept_id_to_exclude = concept_id_to_exclude
                                                                    , exclude_deleted = True 
                                                                    )
    
    return Response(rows_to_return, status=status.HTTP_200_OK)



#--------------------------------------------------------------------------
# /api/codes/?code_list_id=123
class CodeViewSet(viewsets.ReadOnlyModelViewSet):
    '''
        Get the API output for the list of codes.
        For the specified code_list_id.
        (work only on live version since it is used in edit form)
    '''
    queryset = Code.objects.none()
    serializer_class = CodeSerializer

    def get_queryset(self):
        '''
            Provide the dataset for the view.
            Restrict this to just those codes that are visible to the user.
        '''
        # must have querystring of code_list_id
        code_list_id = self.request.query_params.get('code_list_id', None)
        if code_list_id is None:
            raise Http404
        
        queryset = get_visible_codes(self.request.user, code_list_id)
        return queryset


    def filter_queryset(self, queryset):
        '''
            Override the default filtering.
            By default we get codes ordered by creation date even if
            we provide sorted data from get_queryset(). We have to sort the
            data here.
        '''
        queryset = super(CodeViewSet, self).filter_queryset(queryset)
        return queryset.order_by('code')


#--------------------------------------------------------------------------
#--------------------------------------------------------------------------

'''
    ---------------------------------------------------------------------------
    Additional function-based views to handle specific requests.
    ---------------------------------------------------------------------------
'''
@api_view(['GET'])
def child_concepts(request, pk):
    '''
        Return the children of the specified concept (pk).
    '''
    
    # allow only super user
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if request.method == 'GET':
        concept = Concept.objects.filter(id=pk).exclude(is_deleted=True)
        if concept.count() == 0: raise Http404

        # Use a SQL function to extract this data.
        rows = getConceptTreeByConceptId(pk)
        tree = {
            'id': pk,
            'text': 'root - ' + concept.first().name,
            'children': [],
            'state': {'opened': True}
        }
        treeManager = TreeModelManager()
        if rows:
            treeManager.build_child_tree(tree, pk, rows)

        return Response(tree, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------
@api_view(['GET'])
def parent_concepts(request, pk):
    '''
        Return the parents of the specified concept (pk).
    '''
    
    # allow only super user
    if not request.user.is_superuser:
        raise PermissionDenied
        
    if request.method == 'GET':
        concept = Concept.objects.filter(id=pk).exclude(is_deleted=True)
        if concept.count() == 0: raise Http404

        # Use a SQL function to extract this data.
        rows = getParentConceptTreeByConceptId(pk)
        tree = {
            'text': 'root',
            'children': [],
            'state': {'opened': True}}
        treeManager = TreeModelManager()
        if rows:
            # get concept id by max depth
            max_depth_item = max(rows, key=lambda item: item['level_depth'])
            # build tree from the list of concepts returned
            treeManager.build_parent_tree(tree, max_depth_item['concept_id'], rows)

        return Response(tree, status=status.HTTP_200_OK)


#--------------------------------------------------------------------------
@api_view(['GET']) 
def export_concept_codes(request, pk):
    '''
        Return the unique set of codes and descriptions for the specified
        concept (pk).
    '''
    # Require that the user has access to the base concept.
    validate_access_to_view(request.user, Concept, pk)
    if not (allowed_to_view_children(request.user, Concept, pk)
            and
            chk_deleted_children(request.user, Concept, pk, returnErrors = False)
           ):
        raise PermissionDenied
    #
    if request.method == 'GET':
        concept = Concept.objects.filter(id=pk).exclude(is_deleted=True)
        if concept.count() == 0: raise Http404
        
        rows_to_return = []
        titles = ['code', 'description', 'coding_system', 'concept_id', 'concept_version_id', 'concept_name']
        
        current_concept = Concept.objects.get(pk=pk)

        concept_coding_system = Concept.objects.get(id=pk).coding_system.name
        
        # Use a SQL function to extract this data.
        rows = getGroupOfCodesByConceptId(pk)
        for row in rows:
            rows_to_return.append(ordr(zip(titles,  
                                [
                                    row['code'],  
                                    row['description'].encode('ascii', 'ignore').decode('ascii'),
                                    concept_coding_system,
                                    pk,
                                    current_concept.history.latest().history_id,
                                    current_concept.name,
                                ]
                                )))
    
        return Response(rows_to_return, status=status.HTTP_200_OK)

#--------------------------------------------------------------------------
#disable authentication for this function
@api_view(['GET'])
@authentication_classes([])
@permission_classes([])
def export_published_concept_codes(request, pk, concept_history_id):
    '''
        Return the unique set of codes and descriptions for the specified
        concept (pk),
        for a specific historical concept version (concept_history_id).
    '''

    if not Concept.objects.filter(id=pk).exists():            
        raise PermissionDenied


    if concept_history_id is not None:
        if not Concept.history.filter(id=pk, history_id=concept_history_id).exists():
            raise PermissionDenied

 
    is_published = PublishedConcept.objects.filter(concept_id=pk, concept_history_id=concept_history_id).exists()
    # check if the concept version is published
    if not is_published: 
        raise PermissionDenied 
    
    #----------------------------------------------------------------------
    if request.method == 'GET':
        return get_historical_concept_codes(request, pk, concept_history_id)


#--------------------------------------------------------------------------
@api_view(['GET'])
def export_concept_codes_byVersionID(request, pk, concept_history_id):
    '''
        Return the unique set of codes and descriptions for the specified
        concept (pk),
        for a specific historical concept version (concept_history_id).
    '''
    # Require that the user has access to the base concept.
    # validate access for login site
    validate_access_to_view(request.user, Concept, pk, set_history_id=concept_history_id)

        
#     if concept_history_id is None:
#         # get the latest version
#         concept_history_id = int(Concept.objects.get(pk=pk).history.latest().history_id) 
    
    #----------------------------------------------------------------------
        
    current_concept = Concept.objects.get(pk=pk)

    user_can_export = (allowed_to_view_children(request.user, Concept, pk, set_history_id=concept_history_id)
                        and
                        chk_deleted_children(request.user, Concept, pk, returnErrors = False, set_history_id=concept_history_id)
                        and 
                        not current_concept.is_deleted 
                      )

        
    if not user_can_export:
        raise PermissionDenied    
    #----------------------------------------------------------------------


    if request.method == 'GET':
        return get_historical_concept_codes(request, pk, concept_history_id)


#--------------------------------------------------------------------------
def get_historical_concept_codes(request, pk, concept_history_id):
        
#     concept = Concept.objects.filter(id=pk).exclude(is_deleted=True)
#     if concept.count() == 0: raise Http404
    
    concept_ver = Concept.history.filter(id=pk, history_id=concept_history_id) #.exclude(is_deleted=True)
    if concept_ver.count() == 0: raise Http404
    
    rows_to_return = []
    titles = ['code', 'description', 'coding_system', 'concept_id', 'concept_version_id', 'concept_name']
    
#     current_concept = Concept.objects.get(pk=pk)

    # Use db_util function to extract this data.
    history_concept = getHistoryConcept(concept_history_id)

    concept_coding_system = Concept.history.get(id=pk, history_id=concept_history_id).coding_system.name

    rows = getGroupOfCodesByConceptId_HISTORICAL(pk, concept_history_id)
    for row in rows:
        rows_to_return.append(ordr(zip(titles,  
                            [
                                row['code'],  
                                row['description'].encode('ascii', 'ignore').decode('ascii'),
                                concept_coding_system,
                                pk,
                                concept_history_id,
                                history_concept['name'],
                            ]
                            )))

    return Response(rows_to_return, status=status.HTTP_200_OK)

    
    
#############################################################################
#############################################################################
#############################################################################
#@api_view(['GET', 'POST', 'PUT'])
@api_view(['POST'])
def api_concept_create(request):
    
    # allow only super user (and nor 'ReadOnlyUsers')
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if is_member(request.user, group_name='ReadOnlyUsers'):
        raise PermissionDenied
    
    validate_access_to_create()
     
    user_groups = getGroups(request.user)

    if request.method == 'POST':
        errors_dict = {}
        is_valid = True

        new_concept = Concept()
        new_concept.name = request.data.get('name')  
        new_concept.author = request.data.get('author') 
        new_concept.publication = request.data.get('publication')  
        new_concept.description = request.data.get('description') 
        new_concept.publication_doi = request.data.get('publication_doi')
        new_concept.publication_link = request.data.get('publication_link')  # valid URL 
        new_concept.secondary_publication_links = request.data.get('secondary_publication_links')
        new_concept.source_reference = request.data.get('source_reference')
        new_concept.citation_requirements = request.data.get('citation_requirements')

        new_concept.paper_published = request.data.get('paper_published')
        new_concept.validation_performed = request.data.get('validation_performed')
        new_concept.validation_description = request.data.get('validation_description')
        new_concept.entry_date = datetime.now()
         
        new_concept.created_by = request.user        
        new_concept.owner_access = Permissions.EDIT   # int(request.data.get('ownerAccess'))     
        new_concept.owner_id = request.user.id        # int(request.data.get('owner_id'))     
          
        # handle coding_system
        is_valid_data, err, ret_value = chk_coding_system(request.data.get('coding_system'))
        if is_valid_data:
            new_concept.coding_system = ret_value
        else:
            errors_dict['coding_system'] = err

        
        #  group id 
        is_valid_data, err, ret_value = chk_group(request.data.get('group') , user_groups)
        if is_valid_data:
            group_id = ret_value
            if group_id is None or group_id == "0":
                new_concept.group_id = None
                new_concept.group_access = 1
            else:
                new_concept.group_id = group_id
                # handle group-Access
                is_valid_data, err, ret_value = chk_group_access(request.data.get('group_access'))
                if is_valid_data:
                    new_concept.group_access = ret_value
                else:
                    errors_dict['group_access'] = err
        else:
            errors_dict['group'] = err
            
 
        
        # handle world-access
        is_valid_data, err, ret_value = chk_world_access(request.data.get('world_access'))
        if is_valid_data:
            new_concept.world_access = ret_value
        else:
            errors_dict['world_access'] = err        
        
                  
        
        # handling tags  
        tags = request.data.get('tags')
        is_valid_data, err, ret_value = chk_tags(request.data.get('tags'))
        if is_valid_data:
            tags = ret_value
            if tags:
                new_concept.tags = [int(i) for i in tags]
        else:
            errors_dict['tags'] = err  
                    
                
        #-----------------------------------------------------------
        is_valid_components = False
        is_valid_data, err, ret_value = chk_components_and_codes(request.data.get('components'))
        if is_valid_data:
            is_valid_components = True
            components = ret_value
        else:
            errors_dict['components'] = err  
            
        

        
        # Validation

        errors_concept = {}
        if bool(errors_dict):
            is_valid = False
            
        is_valid_cp = True
        is_valid_cp , errors_concept = isValidConcept(request, new_concept) #??
        
        
        #-----------------------------------------------------------
        if not is_valid or not is_valid_cp:  # errors             
            errors_dict.update(errors_concept)
           # y= {**errors_dict, **errors_concept}
            return Response( #data = json.dumps(errors_dict)
                            data = errors_dict
                            , content_type="json"
                            , status=status.HTTP_406_NOT_ACCEPTABLE
                            )
  
        #-----------------------------------------------------------
        else:
            new_concept.save()
            created_concept = Concept.objects.get(pk=new_concept.pk)
            created_concept.history.latest().delete() 
 
#             #-- Tags -------------------------------             
#             tag_ids = tags  
#             # new_tag_list = tags
#             if tag_ids:
#                 new_tag_list = [int(i) for i in tag_ids]
#                 new_concept.tags = new_tag_list
                  
#             # add tags that have not been stored in db
#             if tag_ids:
#                 for tag_id_to_add in new_tag_list:
#                     ConceptTagMap.objects.get_or_create(concept=new_concept, tag=Tag.objects.get(id=tag_id_to_add), created_by=request.user)
                      
                      
            #-- Components/codelists/codes --------
            for comp in components:
                component = Component.objects.create(
                                    comment=comp['comment'],
                                    component_type=Component.COMPONENT_TYPE_EXPRESSION_SELECT, # fixed since it is the only allowed type (not comp['component_type'])
                                    concept=new_concept,
                                    created_by=request.user,
                                    logical_type=comp['logical_type'],
                                    name=comp['name']
                                    )
                
                code_list = CodeList.objects.create(component=component, description='-')
                codeRegex = CodeRegex.objects.create(
                                    component=component,
                                    code_list=code_list,
                                    regex_type=CodeRegex.SIMPLE,
                                    regex_code='',
                                    column_search=CodeRegex.CODE,
                                    sql_rules=''
                                    )
                row_count = 0
                # create codes
                for row in comp['codes']:
                    row_count += 1
                    # Need to check stripped codes
                    if row['code'].strip() == '':      continue
                    obj, created = Code.objects.get_or_create(
                                    code_list=code_list,
                                    code=row['code'],
                                    defaults={
                                            'description': row['description']
                                        }
                                    )
            #--------------------------------------
            #--------------------------------------
              
            created_concept.changeReason = "Created from API"
            created_concept.save()   
              

            data = {'message': 'Concept created successfully',
                    'id': created_concept.pk
                    }
            return Response(data = data
                            , content_type="text/json-comment-filtered"
                            , status=status.HTTP_201_CREATED
                            )
        
        
#############################################################################
#############################################################################
#@api_view(['GET', 'POST', 'PUT'])
@api_view(['PUT'])
def api_concept_update(request):
    
    # allow only super user (and nor 'ReadOnlyUsers')
    if not request.user.is_superuser:
        raise PermissionDenied
    
    if is_member(request.user, group_name='ReadOnlyUsers'):
        raise PermissionDenied
    
    validate_access_to_create()
     
    user_groups = getGroups(request.user)

    if request.method == 'PUT':
        errors_dict = {}
        is_valid = True
        
        concept_id = request.data.get('id') 
        if not isInt(concept_id):
            errors_dict['id'] = 'concept_id must be a valid id.' 
            return Response( 
                            data = errors_dict
                            , content_type="json"
                            , status=status.HTTP_406_NOT_ACCEPTABLE
                            )
        
        if Concept.objects.filter(pk=concept_id).count() == 0: 
            errors_dict['id'] = 'concept_id not found.' 
            return Response( 
                            data = errors_dict
                            , content_type="json"
                            , status=status.HTTP_406_NOT_ACCEPTABLE
                            )
            
        if not allowed_to_edit(request.user, Concept, concept_id):
            errors_dict['id'] = 'concept_id must be a valid accessible concept id.' 
            return Response( 
                            data = errors_dict
                            , content_type="json"
                            , status=status.HTTP_406_NOT_ACCEPTABLE
                            )
        
        
        update_concept = Concept.objects.get(pk=concept_id)
        update_concept.name = request.data.get('name')  
        update_concept.author = request.data.get('author') 
        update_concept.publication = request.data.get('publication')   
        update_concept.publication_doi = request.data.get('publication_doi')
        update_concept.publication_link = request.data.get('publication_link')  # valid URL 
        update_concept.secondary_publication_links = request.data.get('secondary_publication_links')
        update_concept.source_reference = request.data.get('source_reference')
        update_concept.citation_requirements = request.data.get('citation_requirements')

        update_concept.paper_published = request.data.get('paper_published')
        update_concept.validation_performed = request.data.get('validation_performed')
        update_concept.validation_description = request.data.get('validation_description')
        
        if request.data.get('append_description'):
            update_concept.description =  Concept.objects.get(pk=concept_id).description + "  " + request.data.get('description')
        else:
            update_concept.description = request.data.get('description')
        
        update_concept.modified = datetime.now()        
        update_concept.modified_by = request.user
                
        #update_concept.owner_access = Permissions.EDIT   # int(request.data.get('ownerAccess'))     
        #update_concept.owner_id = request.user.id        # int(request.data.get('owner_id'))     
          
        # handle coding_system
        is_valid_data, err, ret_value = chk_coding_system(request.data.get('coding_system'))
        if is_valid_data:
            update_concept.coding_system = ret_value
        else:
            errors_dict['coding_system'] = err


        
        #  group id 
        is_valid_data, err, ret_value = chk_group(request.data.get('group') , user_groups)
        if is_valid_data:
            group_id = ret_value
            if group_id is None or group_id == "0":
                update_concept.group_id = None
                update_concept.group_access = 1
            else:
                update_concept.group_id = group_id
                # handle group-Access
                is_valid_data, err, ret_value = chk_group_access(request.data.get('group_access'))
                if is_valid_data:
                    update_concept.group_access = ret_value
                else:
                    errors_dict['group_access'] = err
        else:
            errors_dict['group'] = err
            
 
        
        # handle world-access
        is_valid_data, err, ret_value = chk_world_access(request.data.get('world_access'))
        if is_valid_data:
            update_concept.world_access = ret_value
        else:
            errors_dict['world_access'] = err        
        
                  
        
        # handling tags  
        tags = request.data.get('tags')
        is_valid_data, err, ret_value = chk_tags(request.data.get('tags'))
        if is_valid_data:
            tags = ret_value
            if tags:
                update_concept.tags = [int(i) for i in tags]
            else:
                update_concept.tags  = None
        else:
            errors_dict['tags'] = err  
                    
                
        #-----------------------------------------------------------
        is_valid_components = False
        is_valid_data, err, ret_value = chk_components_and_codes(request.data.get('components'))
        if is_valid_data:
            is_valid_components = True
            components = ret_value
        else:
            errors_dict['components'] = err  
            
        

        
        # Validation

        errors_concept = {}
        if bool(errors_dict):
            is_valid = False
            
        is_valid_cp = True
        is_valid_cp , errors_concept = isValidConcept(request, update_concept) #??
        
        
        #-----------------------------------------------------------
        if not is_valid or not is_valid_cp:  # errors             
            errors_dict.update(errors_concept)
           # y= {**errors_dict, **errors_concept}
            return Response( #data = json.dumps(errors_dict)
                            data = errors_dict
                            , content_type="json"
                            , status=status.HTTP_406_NOT_ACCEPTABLE
                            )
  
        #-----------------------------------------------------------
        else:
            # update ...
#             #-- Tags -------------------------------------------    
#             # get tags
#             tag_ids = tags  
#             new_tag_list = []
#             if tag_ids:
#                 # split tag ids into list
#                 new_tag_list = [int(i) for i in tag_ids]
#             # save the tag ids
#             old_tag_list = list(ConceptTagMap.objects.filter(concept=update_concept).values_list('tag', flat=True))
#             # detect tags to add
#             tag_ids_to_add = list(set(new_tag_list) - set(old_tag_list))
#             # detect tags to remove
#             tag_ids_to_remove = list(set(old_tag_list) - set(new_tag_list))
#             # add tags that have not been stored in db
#             for tag_id_to_add in tag_ids_to_add:
#                 ConceptTagMap.objects.get_or_create(concept=update_concept, tag=Tag.objects.get(id=tag_id_to_add), created_by=request.user)
#             # remove tags no longer required in db
#             for tag_id_to_remove in tag_ids_to_remove:
#                 tag_to_remove = ConceptTagMap.objects.filter(concept=update_concept, tag=Tag.objects.get(id=tag_id_to_remove))
#                 tag_to_remove.delete()
#             #-----------------------------------------------------
         
                  
            # DELETE ALL EXISTING COMPONENTS FIRST SINCE THERE IS NO MAPPING
            # get all the components attached to the concept
            old_components = update_concept.component_set.all()        
            for old_comp in old_components:
                old_comp.delete()
                
            # insert as new
            #-- Components/codelists/codes --------
            for comp in components:
                component = Component.objects.create(
                                    comment=comp['comment'],
                                    component_type=Component.COMPONENT_TYPE_EXPRESSION_SELECT, # fixed since it is the only allowed type (not comp['component_type'])
                                    concept=update_concept,
                                    created_by=request.user,
                                    logical_type=comp['logical_type'],
                                    name=comp['name']
                                    )
                
                code_list = CodeList.objects.create(component=component, description='-')
                codeRegex = CodeRegex.objects.create(
                                    component=component,
                                    code_list=code_list,
                                    regex_type=CodeRegex.SIMPLE,
                                    regex_code='',
                                    column_search=CodeRegex.CODE,
                                    sql_rules=''
                                    )
                row_count = 0
                # create codes
                for row in comp['codes']:
                    row_count += 1
                    # Need to check stripped codes
                    if row['code'].strip() == '':      continue
                    obj, created = Code.objects.get_or_create(
                                    code_list=code_list,
                                    code=row['code'],
                                    defaults={
                                            'description': row['description']
                                        }
                                    )
            #--------------------------------------
            #--------------------------------------
              
            update_concept.changeReason = "Updates from API"
            update_concept.save()   

            # Get all the 'parent' concepts i.e. those that include this one,
            # and add a history entry to those that this concept has been updated.
            saveDependentConceptsChangeReason(update_concept.pk , "Component concept #" + str(update_concept.pk) + " was updated")
        

            data = {'message': 'Concept updated successfully',
                    'id': update_concept.pk
                    }
            return Response(data = data
                            , content_type="text/json-comment-filtered"
                            , status=status.HTTP_201_CREATED
                            )
        
        
##################################################################################
# search my concepts / published ones

#--------------------------------------------------------------------------
#disable authentication for this function
@api_view(['GET'])
@authentication_classes([])
@permission_classes([]) 
def published_concepts(request):
    '''
        Get the API output for the list of published concepts.
    '''
    return  getConcepts(request, is_authenticated_user=False)
    
#--------------------------------------------------------------------------
@api_view(['GET'])
def myConcepts(request):
    '''
        Get the API output for the list of my concepts.
    '''
    return  getConcepts(request, is_authenticated_user=True)
    
#--------------------------------------------------------------------------
#disable authentication for this function
@api_view(['GET'])
@authentication_classes([])
@permission_classes([]) 
def getConcepts(request, is_authenticated_user=True):    
    search = request.query_params.get('search', '')
    concept_id = request.query_params.get('id', None)
    tag_ids = request.query_params.get('tag_ids', '')
    owner = request.query_params.get('owner_username', '')
    show_only_my_concepts = request.query_params.get('show_only_my_concepts', "0")
    show_deleted_concepts = request.query_params.get('show_deleted_concepts', "0")
    show_only_validated_concepts = request.query_params.get('show_only_validated_concepts', "0")
    concept_brand = request.query_params.get('brand', "")
    author = request.query_params.get('author', '')
    do_not_show_versions = request.query_params.get('do_not_show_versions', "0")
    expand_published_versions = 0   # disable this option
    #expand_published_versions = request.query_params.get('expand_published_versions', "1")
    show_live_and_or_published_ver = "3" #request.query_params.get('show_live_and_or_published_ver', "3")      # 1= live only, 2= published only, 3= live+published
    must_have_published_versions = request.query_params.get('must_have_published_versions', "0")
    
     
    search_tag_list = []
    tags = []
    
    filter_cond = " 1=1 "
    exclude_deleted = True
    get_live_and_or_published_ver = 3   # 1= live only, 2= published only, 3= live+published
    show_top_version_only = True
    
    if tag_ids:
        # split tag ids into list
        search_tag_list = [str(i) for i in tag_ids.split(",")]
        tags = Tag.objects.filter(id__in=search_tag_list)
        filter_cond += " AND tags && '{" + ','.join(search_tag_list) + "}' "
        
    # check if it is the public site or not
    if is_authenticated_user:
        # ensure that user is only allowed to view/edit the relevant concepts
           
        get_live_and_or_published_ver = 3
        if must_have_published_versions == "1":
            get_live_and_or_published_ver = 2
            
#         if show_live_and_or_published_ver in ["1", "2", "3"]:
#             get_live_and_or_published_ver = int(show_live_and_or_published_ver)   #    2= published only
#         else:
#             return Response([], status=status.HTTP_200_OK)   
         
        # show only concepts created by the current user
        if show_only_my_concepts == "1":
            filter_cond += " AND owner_id=" + str(request.user.id)
    
        # if show deleted concepts is 1 then show deleted concepts
        if show_deleted_concepts != "1":
            exclude_deleted = True
        else:
            exclude_deleted = False    
        

      
    else:
        # show published concepts
        get_live_and_or_published_ver = 2   #    2= published only
        
        if PublishedConcept.objects.all().count() == 0:
            return Response([], status=status.HTTP_200_OK)

    
    if expand_published_versions == "1":
        show_top_version_only = False
        
    

    if concept_id is not None:
        if concept_id != '':
            filter_cond += " AND id=" + concept_id
            
    if owner is not None:
        if owner !='':
            if User.objects.filter(username__iexact = owner.strip()).exists():
                owner_id = User.objects.get(username__iexact = owner.strip()).id
                filter_cond += " AND owner_id=" + str(owner_id)
            else:
                # username not found
                filter_cond += " AND owner_id= -1 "


    # if show_only_validated_concepts is 1 then show only concepts with validation_performed=True
    if show_only_validated_concepts == "1":
        filter_cond += " AND COALESCE(validation_performed, FALSE) IS TRUE "

    # show concepts for a specific brand
    if concept_brand != "":
        if Brand.objects.all().filter(name__iexact = concept_brand.strip()).exists():
            current_brand = Brand.objects.all().filter(name__iexact = concept_brand.strip())
            group_list = list(current_brand.values_list('groups', flat=True))
            filter_cond += " AND group_id IN("+ ', '.join(map(str, group_list)) +") "
        else:
            # brand name not found
            filter_cond += " AND group_id IN(-1) "
       
    concepts_srch = get_visible_live_or_published_concept_versions(request
                                                , get_live_and_or_published_ver = get_live_and_or_published_ver 
                                                , searchByName = search
                                                , author = author
                                                , exclude_deleted = exclude_deleted
                                                , filter_cond = filter_cond
                                                , show_top_version_only = show_top_version_only
                                                )
     

    rows_to_return = []
    titles = ['concept_id', 'concept_name'
            , 'version_id'
            , 'author', 'coding_system', 'owner'
            , 'created_by', 'created_date'  
            , 'modified_by', 'modified_date'  
            , 'is_deleted', 'deleted_by', 'deleted_date'
            , 'is_published'
            ]
    if do_not_show_versions != "1":
        titles += ['versions']
    

    for c in concepts_srch:
        ret = [
                c['id'],  
                c['name'].encode('ascii', 'ignore').decode('ascii'),
                c['history_id'],                
                c['author'],
                c['coding_system_name'],
                c['owner_name'],
                
                c['created_by_username'],
                c['created'],
            ]

        if (c['modified_by_id']):
            ret += [c['modified_by_username']]
        else:
            ret += [None]
            
        ret += [
                c['modified'],  
                
                c['is_deleted'],  
            ]
        
        if (c['is_deleted'] == True):
            ret += [c['deleted_by_username']]
        else:
            ret += [None]
        
        ret += [c['deleted'], c['published']]
        
        if do_not_show_versions != "1":
            ret += [get_visible_versions_list(request, Concept, c['id'], is_authenticated_user)]
        
        rows_to_return.append(ordr(zip(titles,  ret )))
                                   
    return Response(rows_to_return, status=status.HTTP_200_OK)                                   


                                                
                                                
# show concept detail
#============================================================= 
@api_view(['GET'])
def myConcept_detail(request, pk, concept_history_id=None, get_versions_only=None):
    ''' 
        Display the detail of a concept at a point in time.
    '''
    
    if Concept.objects.filter(id=pk).count() == 0: 
        raise Http404
    
    if concept_history_id is not None:
        concept_ver = Concept.history.filter(id=pk, history_id=concept_history_id) 
        if concept_ver.count() == 0: raise Http404
        
        
    # validate access concept
    if not allowed_to_view(request.user, Concept, pk, set_history_id=concept_history_id):
        raise PermissionDenied
    
    # we can remove this check as in concept-detail
    #---------------------------------------------------------
    # validate access to child concepts 
    if not (allowed_to_view_children(request.user, Concept, pk, set_history_id=concept_history_id)
            and
            chk_deleted_children(request.user, Concept, pk, returnErrors = False, set_history_id=concept_history_id)
           ):
        raise PermissionDenied
    #---------------------------------------------------------
            
    if concept_history_id is None:
        # get the latest version
        concept_history_id = Concept.objects.get(pk=pk).history.latest().history_id 
        
                    
    return getConceptDetail(request, pk, concept_history_id, is_authenticated_user=True, get_versions_only=get_versions_only)
    
#--------------------------------------------------------------------------
#disable authentication for this function
@api_view(['GET'])
@authentication_classes([])
@permission_classes([]) 
def myConcept_detail_PUBLIC(request, pk, concept_history_id=None, get_versions_only=None):
    ''' 
        Display the detail of a published concept at a point in time.
    '''
    
    if Concept.objects.filter(id=pk).count() == 0: 
        raise Http404
    
    if concept_history_id is not None:
        concept_ver = Concept.history.filter(id=pk, history_id=concept_history_id) 
        if concept_ver.count() == 0: raise Http404
        
            
    if concept_history_id is None:
        # get the latest version
        concept_history_id = Concept.objects.get(pk=pk).history.latest().history_id 
        
    is_published = checkIfPublished(Concept, pk, concept_history_id)
    # check if the concept version is published
    if not is_published and get_versions_only != '1': 
        raise PermissionDenied 
                    
    return getConceptDetail(request, pk, concept_history_id, is_authenticated_user=False, get_versions_only=get_versions_only)
    
        
#--------------------------------------------------------------------------
def getConceptDetail(request, pk, concept_history_id=None, is_authenticated_user=True, get_versions_only=None):
    
    if get_versions_only is not None:
        if get_versions_only == '1':
            titles = ['versions']
            ret = [get_visible_versions_list(request, Concept, pk, is_authenticated_user)]
            rows_to_return = []
            rows_to_return.append(ordr(zip(titles,  ret )))
            return Response(rows_to_return, status=status.HTTP_200_OK)   
    #--------------------------
            
    concept = getHistoryConcept(concept_history_id)
    # The history concept contains the owner_id, to provide the owner name, we
    # need to access the user object with that ID and add that to the concept.
    concept['owner'] = None
    if concept['owner_id'] is not None:
        concept['owner'] = User.objects.get(pk=concept['owner_id']).username

    concept['group'] = None
    if concept['group_id'] is not None: 
        concept['group'] = Group.objects.get(pk=concept['group_id']).name


    concept_history_date = concept['history_date']
    components = getHistoryComponents(pk, concept_history_date)
    
    tags =  []
    concept_tags = concept['tags']
    if concept_tags:
        tags = list(Tag.objects.filter(pk__in=concept_tags).values('description', 'id'))
        
#     tags =  []
#     tags_comp = getHistoryTags(pk, concept_history_date)
#     if tags_comp:
#         tag_list = [i['tag_id'] for i in tags_comp if 'tag_id' in i]
#         tags = list(Tag.objects.filter(pk__in=tag_list).values('description', 'id'))
    
    
    rows_to_return = []
    titles = [
              'concept_id', 'concept_name', 'version_id'
            , 'tags'
            , 'author'
            , 'entry_date'
            , 'description'
            , 'coding_system'
            
            , 'created_by', 'created_date'  
            , 'modified_by', 'modified_date'  
            
            , 'validation_performed' 
            , 'validation_description'
            , 'publication_doi'
            , 'publication_link'
            , 'secondary_publication_links'
            , 'paper_published'
            , 'source_reference'
            , 'citation_requirements'
            
            , 'owner', 'owner_access'
            , 'group', 'group_access'
            , 'world_access'
            
            , 'is_deleted'  # may come from concept live version / or history
            # , 'deleted_by', 'deleted_date' # no need here
            
            , 'components'
            , 'versions'
            ]
    
    ret = [
            concept['id'],
            concept['name'].encode('ascii', 'ignore').decode('ascii'),
            concept['history_id'],
            tags,
            concept['author'],
            concept['entry_date'],
            concept['description'],
            concept['coding_system_name'],
            
            concept['created_by_username'],
            concept['created'],   
            concept['modified_by_username'],
            concept['modified'],

            concept['validation_performed'],
            concept['validation_description'],
            concept['publication_doi'],
            concept['publication_link'],
            concept['secondary_publication_links'],
            concept['paper_published'],
            concept['source_reference'],
            concept['citation_requirements'],
            
            concept['owner'] ,
            dict(Permissions.PERMISSION_CHOICES)[concept['owner_access']],
            concept['group'],
            dict(Permissions.PERMISSION_CHOICES)[concept['group_access']],
            dict(Permissions.PERMISSION_CHOICES)[concept['world_access']],
        ]
    
    # may come from concept live version / or history    
    if (concept['is_deleted'] == True or Concept.objects.get(pk=pk).is_deleted==True):
        ret += [True]
    else:
        ret += [None]
            

    # components
    com_titles = ['name', 'comment', 'component_type', 'logical_type', 
                  'concept_ref_id', 'concept_ref_history_id', 
                  'codes']
    
    ret_components = []
    for com in components:
        # each component already contains the logical_type and codes
        codes = com['codes']
        
        ret_codes = []
        for code in codes:
            ret_codes.append(ordr(zip(
                                        ['code', 'description']
                                        ,  [code['code'], code['description']] 
                                    )
                                )
                            )
            
        ret_comp_data = [com['name'], 
                        com['comment'],
                        dict(Component.COMPONENT_TYPES)[com['component_type']],
                        com['get_logical_type_display'],
                        com['concept_ref_id'],
                        com['concept_ref_history_id'],
                        ret_codes
                        ]
        ret_components.append(ordr(zip(com_titles,  ret_comp_data )))


    #ret += [components]
    ret += [ret_components]
    
    ret += [get_visible_versions_list(request, Concept, pk, is_authenticated_user)]
    
    rows_to_return.append(ordr(zip(titles,  ret )))
                                   
    return Response(rows_to_return, status=status.HTTP_200_OK)                
    
    
    
    
    

    
                    