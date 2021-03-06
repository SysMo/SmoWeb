var smoGui = {io: {json: {}}};

// Sets behaviour for actions on the figure 
smoGui.FigureEditPolicy = draw2d.policy.figure.FigureEditPolicy.extend({
	NAME : "smoGui.FigureEditPolicy",
	
	onRightMouseDown:function(figure, x, y, shiftKey, ctrlKey){
		this._super(figure, x, y, shiftKey, ctrlKey);
		$.contextMenu({
			selector: 'body',
			reposition: false,
			events: {  
				hide: function() {
					$.contextMenu('destroy');
				}
			},
            callback: $.proxy(function(key, options) {
            	switch(key){
					case "properties":
						this.editProperties();
						break;
					case "delete":
						// without undo/redo support
						// this.getCanvas().remove(this)
						// with undo/redo support
						this.removeFromScope();
						var cmd = new draw2d.command.CommandDelete(this);
						this.getCanvas().getCommandStack().execute(cmd);						
					default:
						break;
            	}
            
            }, figure),
            x: x,
            y: y,
            items: 
            {
                "properties":    {name: "Properties", icon: "edit"},
//                "sep1":   "---------",
                "delete": {name: "Delete", icon: "delete"}
            }
        });
	}
});

// Sets behaviour for keyboard actions
smoGui.KeyboardPolicy = draw2d.policy.canvas.KeyboardPolicy.extend({

    NAME : "smoGui.KeyboardPolicy",
    
    /**
     * @constructor 
     */
    init: function(){
        this._super();
    },
    
    onKeyDown:function(canvas, keyCode, shiftKey, ctrlKey){
        // the DEL key
        if(keyCode===46 && canvas.getCurrentSelection()!==null){
            // create a single undo/redo transaction if the user delete more than one element. 
            // This happens with command stack transactions.
            //
            canvas.getCommandStack().startTransaction(draw2d.Configuration.i18n.command.deleteShape);
            canvas.getSelection().each(function(index, figure){
               if (!(figure instanceof draw2d.Connection)) {
            	   figure.removeFromScope();
               }
               var cmd = figure.createCommand(new draw2d.command.CommandType(draw2d.command.CommandType.DELETE));
               if(cmd!==null){
                   canvas.getCommandStack().execute(cmd);
               }
           });
           // execute all single commands at once.
           canvas.getCommandStack().commitTransaction();
        }
        else{
            this._super(canvas, keyCode, shiftKey, ctrlKey);
         }
        
    }


});

// Custom SVG figure
smoGui.SVGFigure = draw2d.SVGFigure.extend({
	
	NAME : "smoGui.SVGFigure",
	
	// Custom port
	SmoPortLocator : draw2d.layout.locator.PortLocator.extend({
		// Port location is set as relative within the figure
		init: function(x_frac, y_frac){
            this._super();
			this.x_frac = x_frac;
			this.y_frac = y_frac;			
        },
		relocate:function(index, port){
			var x = port.getParent().getWidth() * this.x_frac;
			var y = port.getParent().getHeight() * this.y_frac;
            this.applyConsiderRotation(port, x, y);
        }
	}),
	
	init : function(attr, setter, getter)
	{
		this._super(attr, setter, getter);
		// Creating the ports
		for (var i=0; i<this.ports.length; i++) {
			var portLocator =  new this.SmoPortLocator(this.ports[i][2][0], this.ports[i][2][1]);
			var port = this.createPort(this.ports[i][1], portLocator);
			port.setName(this.ports[i][0]);
    	}
		// Installing custom figure edit policy
		this.installEditPolicy(new smoGui.FigureEditPolicy());
	},
	
	// Adding to the angular scope
	addToScope : function() {
        // default values are taken from the definitions
		if (this.values === undefined) {
        	this.values = this.superGroupSet.defaultValues;
        }
        
        var canvas = this.getCanvas();
        canvas.app.components[this.name] = this;
        canvas.app.scope.$digest();
	},
	
	// Removing from the angular scope
	removeFromScope : function() {
		var canvas = this.getCanvas();
		delete canvas.app.components[this.name];
		canvas.app.scope.$digest();
	},
	
	editProperties : function() {
		$( '#' + this.id + '-modal').modal( "show" );
	},

});

// The overall structure of the GUI
smoGui.Application = Class.extend({
	
	NAME : "smoGui.Application",
	// Canvas is linked with app and with figures
	smoCanvas : draw2d.Canvas.extend({
		NAME : "smoCanvas",
		init:function(id, app){
			this._super(id, 500,500);
			this.setScrollArea("#"+id);
			this.setDimension({"width": $("#"+id).width(), "height": $("#"+id).height()});
			this.app = app;
			// Uninstalling default keyboard policy and installing a custom one
			this.uninstallEditPolicy("draw2d.policy.canvas.DefaultKeyboardPolicy");
			this.installEditPolicy(new smoGui.KeyboardPolicy());
			this.id = id;
			// counts up on every figure creation
			this.count = 1;
		}
	}),
	// Console is linked with app
	smoConsole : Class.extend({
		NAME : "smoConsole",
		init:function(app, consoleIdSelector)
		{
			this.app = app;
			this.consoleIdSelector = consoleIdSelector;
			var log= function(msg){
				$(consoleIdSelector).prepend($("<div>"+new Date().toTimeString().replace(/.*(\d{2}:\d{2}:\d{2}).*/, "$1")+" - "+msg+"</div>"));
			};
			this.app.canvas.on("figure:add", function(emitter, event){
				log("Figure added");
			});
			this.app.canvas.on("figure:remove", function(emitter, event){
				log("Figure removed");
			});
			this.app.canvas.on("select", function(emitter, event){
				log("Figure selected: "+event);
			});
			
			// use figure.on("dblclick",..) if want determine the related figure...
			this.app.canvas.on("dblclick", function(emitter, event){
				log("double click: "+JSON.stringify(event));
			});
			this.app.canvas.on("click", function(emitter, event){
				log("click: "+JSON.stringify(event));
			});
			this.app.canvas.on("contextmenu", function(emitter, event){
				log("Context Menu: "+JSON.stringify(event));
			});
		},
		// Emptying console
		clear:function()
		{
			$(this.consoleIdSelector).empty();
		}	
	}),
	// UI List containing draggable items to create components; it is linked with app
	smoUiList : Class.extend({
		NAME : "smoUiList",
		init:function(app, listIdSelector)
		{
			//Creating list items
			var componentTypeNames = app.getComponentTypeNames();
			$.each(componentTypeNames, function(index, element){
				$(listIdSelector).append('<li id="' + element + '">' + element + '</li>');
			});
			
			// Enabling dragging of list items
			$(listIdSelector + ' > li').each(function(index, element){
				$(element)
				.draggable({
							appendTo: "body",
							helper: "clone",
							start: function(e, ui)
							{
								$(this).draggable("option", "revert", true);
								$(ui.helper).css("list-style-type", "none");
							},
				});
			});
			// Enabling dropping on canvas
			$('#' + app.canvas.id).droppable({
				accept: listIdSelector + ' > li',
				drop: function( event, ui ) {
					var component;
					var	name;
					var cloneOffset = ui.helper.offset();
					var listItemId = ui.draggable.context.id; // id of li element; is the same as component type
					$('#'+listItemId).draggable("option", "revert", false);
					//Ensuring unique default component name
					while (("Component" +app.canvas.count) in app.components) {
						app.canvas.count++;
					};
					// Creating the component
					component = eval('new app.componentTypes.' + listItemId + '()');
					// Prompting the user for a name of the component
					do {
						name = prompt("Please enter component name", "Component" + app.canvas.count);
					} while (name == "");
					if (name == null) {
						return;
					}
					component.name = name;
					component.type = listItemId;
					// Adding the figure to the canvas
					app.canvas.add(component, cloneOffset.left - app.canvas.getAbsoluteX(), 
					cloneOffset.top - app.canvas.getAbsoluteY());
					// Adding the component to the angular scope
					component.addToScope();
				}
			});
		}
	}),
	
	init : function(name, scope) 
	{
		this.name = name;
		// App is linked with scope
		this.scope = scope;
		// General scope object for angular, e.g. for ng-repeat
		this.components = {};
		this.canvas = null;
		this.console = null;
		this.componentTypes = null;
	},
	
	addCanvas : function(id)
	{
		this.canvas = new this.smoCanvas(id, this);
	},
	addConsole : function(consoleIdSelector)
	{
		this.console = new this.smoConsole(this, consoleIdSelector);
	},
	addComponentTypes : function(defs)
	{
		this.componentTypes = new smoGui.io.json.componentsReader().read(defs);
	},
	createUIList : function(listIdSelector)
	{
		new this.smoUiList(this, listIdSelector);
	},
	addCircuit: function(json){
		new smoGui.io.json.circuitReader().unmarshal(this, json);
	}, 
	exportCircuit: function(){
		new smoGui.io.json.circuitWriter().marshal(this, function(json){
			console.log(json);
		});
	}, 
	getComponentTypeNames : function()
	{
		return Object.keys(this.componentTypes);
	}
});