smoGui.jsonReader = draw2d.io.json.Reader.extend({
    
    NAME : "smoGui.jsonReader",
    
    init: function(){
        this._super();
    },
    
    /**
     * @method
     * 
     * Restore the canvas from a given JSON object.
     * 
     * @param {draw2d.Canvas} canvas the canvas to restore
     * @param {Object} document the json object to load.
     */
    unmarshal: function(canvas, json){
        var result = new draw2d.util.ArrayList();
        
        if(typeof json ==="string"){
            json = JSON.parse(json);
        }

        var node=null;
        $.each(json, $.proxy(function(i, element){
            try{
            	var portsData = {};
            	if (typeof element.attrs.ports !== 'undefined') {
	            	eval('var portsData = ' + JSON.stringify(element.attrs.ports));    	
            	}
            	eval('smoGui.shapes.' + element.type + ' = ' +
            			element.extendsWhich + '.extend({\
                    		NAME : "' + element.type + '",\
                    		init : function(attr)\
                    		{\
                    			this._super('+JSON.stringify(element.attrs)+');\
                    			for (var portType in portsData) {\
            	            		for (var n=1; n<=portsData[portType]; n++) {\
            	            			this.addPort(eval("new draw2d." + portType + "()"));\
            	            		}\
            	            	}\
                    			this.installEditPolicy(new smoGui.FigureEditPolicy());\
                    		}\
                    	});'
            	);            	
                var o = eval("new smoGui.shapes."+element.type+"()");
                var source= null;
                var target=null;
                for(i in element){
                    var val = element[i];
                    if(i === "source"){
                        node = canvas.getFigure(val.node);
                        if(node===null){
                            throw "Source figure with id '"+val.node+"' not found";
                        }
                        source = node.getPort(val.port);
                        if(source===null){
                            throw "Unable to find source port '"+val.port+"' at figure '"+val.node+"' to unmarschal '"+element.type+"'";
                        }
                    }
                    else if (i === "target"){
                        node = canvas.getFigure(val.node);
                        if(node===null){
                            throw "Target figure with id '"+val.node+"' not found";
                        }
                        target = node.getPort(val.port);
                        if(target===null){
                            throw "Unable to find target port '"+val.port+"' at figure '"+val.node+"' to unmarschal '"+element.type+"'";
                        }
                    }
                    else if (i === "properties"){
                    	
                    }
                }
                if(source!==null && target!==null){
                    o.setSource(source);
                    o.setTarget(target);
                }
                o.setPersistentAttributes(element);
                canvas.add(o);
                result.add(o);
            }
            catch(exc){
                debug.error(element,"Unable to instantiate figure type '"+element.type+"' with id '"+element.id+"' during unmarshal by "+this.NAME+". Skipping figure..");
                debug.error(exc);
                debug.warn(element);
            }
        },this));
        
        // restore group assignment
        //
        $.each(json, $.proxy(function(i, element){
            if(typeof element.composite !== "undefined"){
               var figure = canvas.getFigure(element.id);
               if(figure===null){
                   figure =canvas.getLine(element.id);
               }
               var group = canvas.getFigure(element.composite);
               group.assignFigure(figure);
            }
        },this));
        
        // recalculate all crossings and repaint the connections with 
        // possible crossing decoration
        canvas.calculateConnectionIntersection();
        canvas.getLines().each(function(i,line){
            line.svgPathString=null;
            line.repaint();
        });
        canvas.linesToRepaintAfterDragDrop = canvas.getLines().clone();

        canvas.showDecoration();
        
        return result;
    }
});