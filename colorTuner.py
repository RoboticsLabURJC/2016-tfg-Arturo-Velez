import MyOpenCV


class colorTuner

	def tune(input_image, h, s, v)
		#OJO!!! hay que controlar esto para que los valores sean correctos
		hmax= h + 1
		hmin = h -1
		smax = s + 1
		smin = s - 1
		vmax = v + 1
		vmin = v - 1
		
		MyOpenCV.colorfilter(input_image, hmax, hmin, smax, smin, vmax, vmin)

