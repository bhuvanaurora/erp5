##parameters=form_id,cancel_url,dialog_method,selection_name,dialog_id,previous_md5_object_uid_list=None

# Updates attributes of an Zope document
# which is in a class inheriting from ERP5 Base


from Products.Formulator.Errors import ValidationError, FormValidationError
from string import join
from ZTUtils import make_query

request=context.REQUEST

#Exceptions for Workflow
if dialog_method == 'workflow_status_modify':
  return context.workflow_status_modify(form_id=form_id,
                                        dialog_id=dialog_id
                                        )

error_message = ''

try:
  # Validate the form
  form = getattr(context,dialog_id)
  form.validate_all_to_request(request)
  kw = {}
  for f in form.get_fields():
    k = f.id
    v = getattr(request,k,None)
    if v is not None:
      k = k[3:]
      kw[k] = v
  url_params = []
  # Object view params
  kw['form_id'] = form_id
  kw['dialog_id'] = dialog_id
  kw['selection_name'] = selection_name
  # Check if the selection did not changed
  if previous_md5_object_uid_list is not None:
    selection_list = context.portal_selections.callSelectionFor(selection_name, context=context)
    if selection_list is not None:
      object_uid_list = map(lambda x:x.getObject().getUid(),selection_list)
      error = context.portal_selections.selectionHasChanged(previous_md5_object_uid_list,object_uid_list)
      if error:
        error_message = 'Sorry+your+selection+has+changed'
  url_params_string = make_query(**kw)
except FormValidationError, validation_errors:
  # Pack errors into the request
  field_errors = form.ErrorFields(validation_errors)
  request.set('field_errors', field_errors)
  return form(request)

if error_message != '':
  redirect_url = '%s/%s?%s' % ( context.absolute_url(), form_id
                                , 'portal_status_message=%s' % error_message
                                )
elif url_params_string != '':
  redirect_url = '%s/%s?%s' % ( context.absolute_url()
                            , dialog_method
                            , url_params_string
                            )
else:
  redirect_url = '%s/%s' % ( context.absolute_url()
                            , dialog_method
                            )

return request.RESPONSE.redirect( redirect_url )
