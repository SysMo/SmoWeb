var MyRectangle = draw2d.shape.basic.Rectangle.extend({
	init : function(attr)
	{
		this._super($.extend({bgColor:'green'},attr));
		this.addPort(new draw2d.OutputPort());
	}
});
var MyCircle = draw2d.shape.basic.Circle.extend({
	init : function(attr)
	{
		this._super($.extend({bgColor:'blue'},attr));
		this.addPort(new draw2d.InputPort());
	}
});