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
		this.writer = new draw2d.io.json.Writer();
		this.json = null;
		this.appName = null;
	},
	loadFromJson: function(json){
		this.json = $.extend(true, {}, json);
		new smoGui.io.json.circuitsReader().unmarshal(this, json);
	},
	updateJson: function(){
		var canvas = this;
		this.writer.marshal(canvas, function(json){
			canvas.json = json;
		});
	},
	getJson: function(){
		return this.json;
	}
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
smoGui.Application = Class.extend({
	NAME : "smoGui.Application",
	init : function(name) 
	{
		this.name = name;	
		this.components = null;
	},
	addCanvas : function(id, dimensions)
	{
		this.canvas = new smoGui.Canvas(id);
		this.canvas.setDimension(dimensions);
		this.canvas.appName = this.name;
		this.console = new smoGui.Console(this.canvas);
	},
	addComponents : function(defs)
	{
		this.components = new smoGui.io.json.componentsReader().read(defs);
	}
});