var smoGui = {};

//smoGui.CanvasPolicy = draw2d.policy.canvas.CanvasPolicy.extend({
	//NAME : "smoGui.CanvasPolicy",
	//onMouseDown:function(canvas, x, y, shiftKey, ctrlKey){
		//this._super( canvas, x, y, shiftKey, ctrlKey);
		//canvas.updateJson();
		//console.log(canvas.json);
	//},
//});

smoGui.Canvas = draw2d.Canvas.extend({
	NAME : "smoGui.Canvas",
	init:function(id){
		this._super(id, 500,500);
		this.setScrollArea("#"+id);
		this.reader = new draw2d.io.json.Reader();
		this.writer = new draw2d.io.json.Writer();
		this.json = null;
	},
	loadFromJson: function(json){
		this.json = $.extend(true, {}, json);
		this.reader.unmarshal(this, json);
	},
	updateJson: function(){
		var canvas = this;
		this.writer.marshal(canvas, function(json){
			canvas.json = json;
		});
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
	init : function(id) 
	{
		this.canvas = new smoGui.Canvas(id);
		//this.canvas.installEditPolicy(new smoGui.CanvasPolicy());
		this.console = new smoGui.Console(this.canvas);
	}
});