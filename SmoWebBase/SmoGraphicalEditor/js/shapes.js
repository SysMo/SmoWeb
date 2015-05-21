var MyRectangle = draw2d.shape.basic.Rectangle.extend({
	NAME : "MyRectangle",
	init : function(attr)
	{
		this._super($.extend({bgColor:'green'},attr));
		this.addPort(new draw2d.OutputPort());
		this.installEditPolicy(new smoGui.FigureEditPolicy());
		this.properties = {'mass': 3, 'density': 2, 'flow': 5};
	},
	
});
var MyCircle = draw2d.shape.basic.Circle.extend({
	NAME : "MyCircle",
	init : function(attr)
	{
		this._super($.extend({bgColor:'blue'},attr));
		this.addPort(new draw2d.InputPort());
		this.installEditPolicy(new smoGui.FigureEditPolicy());
		this.properties = {'material': 'steel'};
	}
});