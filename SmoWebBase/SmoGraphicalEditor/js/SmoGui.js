var smoGui = {io: {json: {}}};

smoGui.addComponentModal = function(figure) {
	var modalTemplate = '\
		<div id="' + figure.id + '-properties-dialog">\
			<form>\
				<fieldset>';
	for (var property in figure.properties) {
		modalTemplate += '\
		      <label for="' + figure.id + '-' + property + '">' + property + '</label>\
		      <input type="text" + name="' + figure.id + '-' + property + '" id="' + figure.id + '-' + property + '" value="' + String(figure.properties[property]) + '" class="text ui-widget-content ui-corner-all">';
	}
	modalTemplate += '\
		    </fieldset>\
		  </form>\
		</div>';
	$('#component-modals-container').append(modalTemplate);
	$( '#' + figure.id + '-properties-dialog').dialog({
	    autoOpen: false,
	    height: 300,
	    width: 350,
	    modal: true,
	    buttons: {
	      "Update": function(){console.log('Updated');},
	      Cancel: function() {
	        $(this).dialog( "close" );
	      }
	    }
	});
}

smoGui.removeComponentModal = function(figure) {
	$( '#' + figure.id + '-properties-dialog').remove();
}

smoGui.editProperties = function(figure) {
	$( '#' + figure.id + '-properties-dialog').dialog( "open" );
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
						smoGui.editProperties(this);
						break;
					case "delete":
						// without undo/redo support
						// this.getCanvas().remove(this)
						// with undo/redo support
						var cmd = new draw2d.command.CommandDelete(this);
						this.getCanvas().getCommandStack().execute(cmd);
						smoGui.removeComponentModal(this);
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

smoGui.Canvas = draw2d.Canvas.extend({
	NAME : "smoGui.Canvas",
	init:function(id){
		this._super(id, 500,500);
		this.setScrollArea("#"+id);
		this.appName = null;
	},
	dumpToJson: function(){
		var canvas = this;
		new smoGui.io.json.circuitsWriter().marshal(canvas, function(json){
			console.log(json);
		});
	},
});
smoGui.Console = Class.extend({
	NAME : "smoGui.Console",
	init:function(canvas)
	{
		var log= function(msg){
			$("#events").prepend($("<div>"+new Date().toTimeString().replace(/.*(\d{2}:\d{2}:\d{2}).*/, "$1")+" - "+msg+"</div>"));
		};
		canvas.on("figure:add", function(emitter, event){
			log("Figure added");
		});
		canvas.on("figure:remove", function(emitter, event){
			log("Figure removed");
		});
		canvas.on("select", function(emitter, event){
			log("Figure selected: "+event);
		});
		
		// use figure.on("dblclick",..) if want determine the related figure...
		canvas.on("dblclick", function(emitter, event){
			log("double click: "+JSON.stringify(event));
		});
		canvas.on("click", function(emitter, event){
			log("click: "+JSON.stringify(event));
		});
		canvas.on("contextmenu", function(emitter, event){
			log("Context Menu: "+JSON.stringify(event));
		});
	},
	clear:function()
	{
		$("#events").empty();
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
		this.ports = attr["ports"] || [];
		for (var i=0; i<this.ports.length; i++) {
			var portLocator =  new this.SmoPortLocator(this.ports[i][2][0], this.ports[i][2][1]);
			var port = this.createPort(this.ports[i][1], portLocator);
			port.setName(this.ports[i][0]);
    	}
		this.installEditPolicy(new smoGui.FigureEditPolicy());
	},
});


smoGui.Application = Class.extend({
	NAME : "smoGui.Application",
	init : function(name) 
	{
		this.name = name;	
		this.componentTypes = null;
		this.circuit = null;
	},
	addCanvas : function(id, dimensions)
	{
		this.canvas = new smoGui.Canvas(id);
		this.canvas.setDimension(dimensions);
		this.canvas.appName = this.name;
		this.console = new smoGui.Console(this.canvas);
	},
	addComponentTypes : function(defs)
	{
		this.componentTypes = new smoGui.io.json.componentsReader().read(defs);
		return Object.keys(this.componentTypes);
	},
	addCircuit: function(json){
		this.circuit = new smoGui.io.json.circuitsReader().unmarshal(this.canvas, json);
	}, 
	getComponetFigures: function(){
		var componentFigures = [];
		var app = this;
        $.each(this.circuit.components, function(name, id){
        	componentFigures.push(app.canvas.getFigure(id));
        });
		return componentFigures;
	}
});