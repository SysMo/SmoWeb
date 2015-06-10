def draw_networkx_labels(G, pos,
						 labels=None,
						 font_size=12,
						 font_color='k',
						 font_family='sans-serif',
						 font_weight='normal',
						 alpha=1.0,
						 ax=None,
						 **kwds):
	try:
		import matplotlib.pyplot as plt
		import matplotlib.cbook as cb
	except ImportError:
		raise ImportError("Matplotlib required for draw()")
	except RuntimeError:
		print("Matplotlib unable to open display")
		raise

	if ax is None:
		ax = plt.gca()

	if labels is None:
		labels = dict((n, n) for n in G.nodes())

	# set optional alignment
	horizontalalignment = kwds.get('horizontalalignment', 'center')
	verticalalignment = kwds.get('verticalalignment', 'center')
	rotation = kwds.get('rotation', 0)
	text_items = {}  # there is no text collection so we'll fake one
	for n, label in labels.items():
		(x, y) = pos[n]
		if not cb.is_string_like(label):
			label = str(label)  # this will cause "1" and 1 to be labeled the same
		t = ax.text(x, y,
				  label,
				  size=font_size,
				  color=font_color,
				  family=font_family,
				  weight=font_weight,
				  horizontalalignment=horizontalalignment,
				  verticalalignment=verticalalignment,
				  transform=ax.transData,
				  clip_on=True,
				  rotation = rotation
				  )
		text_items[n] = t

	return text_items
