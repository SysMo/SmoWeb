==================
Angular directives
==================

.. highlight:: html

---------
smoButton
---------

Creates a button::
   
   <smo-button action="addRow(i)" icon="plus" tip="Inserts row at i-th index" size="md"></smo-button>

**Restrict:** Element

**Scope:** No

**Parameters:**
   * **action** - The function call on a click event
   * **icon** - The base name of a *.png* file containing the icon of the button
   * **tip** - A tooltip to appear on hover
   * **size** - The width of the button. Valid strings are:
      * 'sm' - 16px, also the default value
      * 'md' - 24px
      * 'lg' - 32px

-----------
smoQuantity
-----------

Visualizes a quantity input or output field with unit conversion functionality. In the case of an input field,
value validation is also performed::
   
   <div smo-quantity view-type="input" field-var="field" smo-data-source="values"></div>

**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **view-type** - The display type of the field. Valid strings are:
      * 'input'
      * 'output'
   * **field-var** - An object defining the field.
   * **smo-data-source** - An object containing the value of the field.  

---------
smoChoice
---------

Visualizes a field for selecting a value from a dropdown list of options::
   
   <div smo-choice field-var="field" smo-data-source="values"></div>

**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **field-var** - An object defining the field, including the list of options.
   * **smo-data-source** - An object containing the value of the field.  

---------
smoString
---------

Visualizes a field for input or output of single- or multi-line strings::
   
   <div smo-string view-type="input" field-var="field" smo-data-source="values"></div>

**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **view-type** - The display type of the field. Valid strings are:
      * 'input'
      * 'output'
   * **field-var** - An object defining the field, including the multi-line option.
   * **smo-data-source** - An object containing the value of the field.  

-------
smoBool
-------

Visualizes a field for handling boolean values. The directive creates a checkbox 
(if ``view-type`` is 'input') or *true*/*false* (if ``view-type`` is 'output')::
   
   <div smo-string view-type="input" field-var="field" smo-data-source="values"></div>

**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **view-type** - The display type of the field. Valid strings are:
      * 'input'
      * 'output'
   * **field-var** - An object defining the field.
   * **smo-data-source** - An object containing the value of the field.  

--------------
smoRecordArray
--------------

Displays a field for the input of an array of records. The structure of the records is a combination of the basic field types.
The array pops up in edit mode when an icon is clicked on by the user::
   
   <div smo-record-array="field" smo-data-source="values"></div>

**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **smo-record-array** - An object defining the field.
   * **smo-data-source** - An object containing the value of the field.  

-------
smoPlot
-------
Displays a plot field. The directive draws a plot of a set of data using the `dygraphs`_ library 
and allows for its export in a *png* format::

   <div smo-plot field-var="field" smo-data-source="values"></div>
   
**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **field-var** - An object defining the field.
   * **smo-data-source** - An object containing the value of the field.


--------
smoTable
--------

Displays a table field. The directive draws a `Google Charts`_ table for a set of data 
and allows for its export in a *csv* file::

   <div smo-table field-var="field" smo-data-source="values"></div>
   
**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **field-var** - An object defining the field.
   * **smo-data-source** - An object containing the value of the field.

-------------
smoFieldGroup
-------------

Visualizes a basic organisation of fields in a group. Each field-group is displayed as a delimited colored area containing 
a label and stacked fields::

   <div smo-field-group="fieldGroup" view-type="input" smo-data-source="smoDataSource"></div>
   
**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **smo-field-group** - An object defining the field-group.
   * **view-type** - The display type of the field-group, which applies to all its fields. Valid strings are:
      * 'input'
      * 'output'
   * **smo-data-source** - An object containing the values of the fields making up the field-group.
   
**Uses:** *smoQuantity*, *smoChoice*, *smoString*, *smoBool*, *smoRecordArray*

------------
smoViewGroup
------------

Displays a grouping of plot and/or table fields. Each view-group is visualized as a delimited area with pill navigation
to the left for switching among the plots and/or tables contained in its fields::

   <div smo-view-group="viewGroup" smo-data-source="smoDataSource"></div>
   
**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **smo-view-group** - An object defining the view-group.
   * **smo-data-source** - An object containing the values of the fields making up the view-group.
   
**Uses:** *smoPlot*, *smoTable*


----------------
smoSuperGroupSet
----------------

Displays a set of super-groups, each of which consists of one or more field-groups and/or view-groups::

   <div smo-super-group-set="superGroupSet" model-name="flowResistanceInputs" view-type="input" smo-data-source="values"></div>

**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **smo-super-group-set** - An object defining the set of super-groups.
   * **model-name** - The name of the model defined by the super-group set.
   * **view-type** - The display type of the super-groups in the set, 
   which applies also to all their field-groups and/or view-groups. Valid strings are:
      * 'input'
      * 'output'
   * **smo-data-source** - An object containing the values of the fields making up the view-group.
   
**Uses:** *smoPlot*, *smoTable*

------------
smoModelView
------------

This directive handles the communication with the server via a communicator object. The communicator is responsible for
sending AJAX requests to carry out specific actions, 
such as fetching the initial data needed to visualise the model or sending input values to make calculations.
Through the communicator, the directive is also able to inform the user about an unsuccessful outcome of the communication 
by displaying error messages::      

   <div smo-model-view="flowResistanceInputs" view-type="input" communicator="flowResistance.inputCommunicator"></div>

**Restrict:** Attribute

**Scope:** Yes

**Parameters:**
   * **smo-model-view** - The name of the model to be visualised.
   * **view-type** - The display type of the model. Valid strings are:
      * 'input'
      * 'output'
   * **communicator** - A communicator object
    
.. _dygraphs: http://dygraphs.com/
.. _Google Charts: https://developers.google.com/chart/