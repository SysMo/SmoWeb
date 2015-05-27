var smoGui = {io: {json: {}}};

smoGui.createUIList = function (app, listIdSelector) {
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
					  $(ui.helper).css("list-style-type", "none");
					},
					stop: function(event, ui) {
						var myShape;
						var	name;
						var cloneOffset = ui.helper.offset();
						var id = $(this).context.id;
						do {
							myShape = eval('new app.componentTypes.' + id + '()');
						} while ((id+myShape.count) in app.circuit.components);
						do {
							name = prompt("Please enter component name", id+myShape.count);
						} while (name == "");
						if (name == null) {
							return;
						}
						myShape.name = name;
						app.circuit.components[name] = myShape;
						app.canvas.add(myShape, cloneOffset.left - app.canvas.getAbsoluteX(), 
						cloneOffset.top - app.canvas.getAbsoluteY());
						myShape.addToScope();
					}
		});
	});
}

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

smoGui.SVGFigure = draw2d.SVGFigure.extend({
	
	NAME : "smoGui.SVGFigure",
	
	SmoPortLocator : draw2d.layout.locator.PortLocator.extend({
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
		for (var i=0; i<this.ports.length; i++) {
			var portLocator =  new this.SmoPortLocator(this.ports[i][2][0], this.ports[i][2][1]);
			var port = this.createPort(this.ports[i][1], portLocator);
			port.setName(this.ports[i][0]);
    	}
		this.installEditPolicy(new smoGui.FigureEditPolicy());
	},
	
	addToScope : function() {
        if (this.values === undefined) {
        	this.values = this.fieldgroup.defaultValues;
        }
        
        var canvas = this.getCanvas();
        canvas.app.circuit.components[this.name] = this;
        canvas.app.scope.$digest();
	},
	
	removeFromScope : function() {
		var canvas = this.getCanvas();
		delete canvas.app.circuit.components[this.name];
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
		},
		dumpToJson: function(){
			var canvas = this;
			new smoGui.io.json.circuitsWriter().marshal(canvas, function(json){
				console.log(json);
			});
		},
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
		clear:function()
		{
			$(this.consoleIdSelector).empty();
		}	
	}),
	// UI List is linked with app
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
							  $(ui.helper).css("list-style-type", "none");
							},
							stop: function(event, ui) {
								var myShape;
								var	name;
								var cloneOffset = ui.helper.offset();
								var id = $(this).context.id;
								do {
									myShape = eval('new app.componentTypes.' + id + '()');
								} while ((id+myShape.count) in app.circuit.components);
								do {
									name = prompt("Please enter component name", id+myShape.count);
								} while (name == "");
								if (name == null) {
									return;
								}
								myShape.name = name;
								app.circuit.components[name] = myShape;
								app.canvas.add(myShape, cloneOffset.left - app.canvas.getAbsoluteX(), 
								cloneOffset.top - app.canvas.getAbsoluteY());
								myShape.addToScope();
							}
				});
			});
		}
	}),
	
	init : function(name, scope) 
	{
		this.name = name;
		// App is linked with scope
		this.scope = scope;
		// General scope object for angular, e.g. for ng-repeat
		this.circuit = {components: {}, connections: []};
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
		new smoGui.io.json.circuitsReader().unmarshal(this, json);
	}, 
	
	getComponentTypeNames : function()
	{
		return Object.keys(this.componentTypes);
	}
});