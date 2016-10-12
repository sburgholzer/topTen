<?php
	$file_handle = fopen("/home/sburgholzer/usTopTenHour.txt", "r");	
	while (!feof($file_handle)) {
		$hour = fgets($file_handle);
	}
	fclose($file_handle);
	
	$item = $_GET["item"];

    if (empty($_GET)) {
		$itemClicked = "Warmest";
	}
	else {
		$itemClicked = $item;
	}
	
	$csvData = file_get_contents('/home/sburgholzer/usWarmest.txt');
	$lines = explode(PHP_EOL, $csvData);
	$warmest = array();
	foreach ($lines as $line) {
		$warmest[] = str_getcsv($line);
	}
	//print_r($array);
	fclose($csvData);

	$csvData = file_get_contents('/home/sburgholzer/usColdest.txt');
	$lines = explode(PHP_EOL, $csvData);
	$coldest = array();
	foreach ($lines as $line) {
		$coldest[] = str_getcsv($line);
	}
	//print_r($array);
	fclose($csvData);
?>
<!doctype html>
<html lang="en">
  <head>
    <style>
      .map {
        width: 1400px;
        height: 900px;
      }
      #map {
        position: relative;
      }
      #info {
        position: absolute;
        height: 1px;
        width: 1px;
        z-index: 100;
      }
      .tooltip.in {
        opacity: 1;
      }
      .tooltip.top .tooltip-arrow {
        border-top-color: white;
      }
      .tooltip-inner {
        border: 2px solid white;
      }
      .popover-content {
        width: 300px;
      }
      #graphs {
      	position: absolute;
      	left: 1410px;
      	top: 0px;
      	width: 500px;
      	height: 971px;
      	background-color: #fff;
      <!--	border-style: solid;
      	border-width: 1px;-->
      }
	  table, th, td {
			border: 1px solid black;
			}
    </style>
    <link rel="stylesheet" href="http://openlayers.org/en/v3.18.1/css/ol.css" type="text/css">
    <script src="https://code.jquery.com/jquery-2.2.3.min.js"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
    <script src="http://openlayers.org/en/v3.18.1/build/ol.js" type="text/javascript"></script>
    <title>Top Ten Warmest and Coldest Stations</title>
  </head>
  <body>
	<h1>Top 10 Warmest and Coldest Stations for <?= $hour ?></h1>

    <div id="map" class="map"></div>
    <div id="graphs">
		<br /><br /><br /><center><a href="usMap.php?item=Warmest">Warmest</a> | <a href="usMap.php?item=Coldest">Coldest</a></center>
		<center>
		<?php
			if ($itemClicked == "Warmest") {
				print('<table cellpadding="10">');
				echo "<caption><b>Top 10 Warmest for $hour</b></caption>";
				print('<tr>
						<th>&nbsp;Station&nbsp;&nbsp;&nbsp;&nbsp;</th>
						<th>&nbsp;Celsius&nbsp;&nbsp;&nbsp;&nbsp;</th>
						<th>&nbsp;Fahrenheit&nbsp;&nbsp;&nbsp;&nbsp;</th>
					</tr>');
				for($i = 0; $i < count($warmest); $i++) {
					print('<tr>');
					for($ii = 0; $ii < count($warmest[$i]); $ii++) {
						if ($ii == 0)
							print('<td><a href= http://weather.gladstonefamily.net/site/search?site=' . $warmest[$i][$ii] . ' target = _blank>&nbsp;'  . $warmest[$i][$ii] . '</td>');
						else
						{
			
							$value = $warmest[$i][$ii];
							$initialData = intval($value);
							$fahrenheit = $initialData * 1.8 + 32;
							//initialData = intval($data[$i][$ii]);
							//$fahrenheit = {intval($data[$i][$ii])} * (9/5) + 32;
							//$fahrenheit = "{$fahrenheit}";
							print("<td>&nbsp;{$warmest[$i][$ii]}&deg;C</td>
							<td>&nbsp;{$fahrenheit}&deg;F</td>");
						}
					}
					print('</tr>');
				}
				print('</table>');		
			}
			else if ($itemClicked == "Coldest") {
				print('<table cellpadding="10">');
				echo "<caption><b>Top 10 Coldest for $hour</b></caption>";
				print('<tr>
						<th>&nbsp;Station&nbsp;&nbsp;&nbsp;&nbsp;</th>
						<th>&nbsp;Celsius&nbsp;&nbsp;&nbsp;&nbsp;</th>
						<th>&nbsp;Fahrenheit&nbsp;&nbsp;&nbsp;&nbsp;</th>
					</tr>');
				for($i = 0; $i < count($coldest); $i++) {
					print('<tr>');
					for($ii = 0; $ii < count($coldest[$i]); $ii++) {
						if ($ii == 0)
							print('<td><a href= http://weather.gladstonefamily.net/site/search?site=' . $coldest[$i][$ii] . ' target = _blank>&nbsp;'  . $coldest[$i][$ii] . '</td>');
						else
						{
			
							$value = $coldest[$i][$ii];
							$initialData = intval($value);
							$fahrenheit = $initialData * 1.8 + 32;
							//initialData = intval($data[$i][$ii]);
							//$fahrenheit = {intval($data[$i][$ii])} * (9/5) + 32;
							//$fahrenheit = "{$fahrenheit}";
							print("<td>&nbsp;{$coldest[$i][$ii]}&deg;C</td>
							<td>&nbsp;{$fahrenheit}&deg;F</td>");
						}
					}
					print('</tr>');
				}
				print('</table>');	
			}
		?>
		</center>
	</div>
    <div style="display: none;">
      <div id="popup" class="popup" style="width: 600px;"></div>
    </div>
    <div id="info"></div>
    <script type="text/javascript">

var coldest = new ol.layer.Vector({
  source: new ol.source.Vector({
    url: 'usColdest.kml',
    format: new ol.format.KML({renderers: ['Canvas', 'VML'],
    extractStyles: true,
    extractAttributes: true,
    maxDepth: 2}),
	wrapX: false
  })
});

var warmest = new ol.layer.Vector({
  source: new ol.source.Vector({
    url: 'usWarmest.kml',
    format: new ol.format.KML({renderers: ['Canvas', 'VML'],
    extractStyles: true,
    extractAttributes: true,
    maxDepth: 2}),
	wrapX: false
  })
});

var attribution = new ol.Attribution({
  html: 'Tiles &copy; <a href="http://services.arcgisonline.com/ArcGIS/' +
      'rest/services/World_Imagery/MapServer">ArcGIS</a>'
});

var mapFeatures = new ol.source.XYZ({
	url: 'http://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
	wrapX: false
});
var FeaturesLayer = new ol.layer.Tile({
	source: mapFeatures
});
var map = new ol.Map({
  target: document.getElementById('map'),
  layers: [
    new ol.layer.Tile({
      source: new ol.source.XYZ({
        url: 'http://server.arcgisonline.com/ArcGIS/rest/services/' +
            'World_Imagery/MapServer/tile/{z}/{y}/{x}',
	wrapX: false
      }),
    }), FeaturesLayer, warmest,  coldest  ],      
  view: new ol.View({
    center: ol.proj.fromLonLat([-98.5795, 39.8282]),
    zoom: 4.5,
  })
});


// Function for graphing display:
/*function imgDisplay(imgPath) {
	var img = document.createElement("IMG");
	img.src = imgPath;
	document.getElementById('graphs').appendChild(img);
}*/

// Stuff for mouse-over below here:

      var info = $('#info');
      info.tooltip({
        animation: false,
        trigger: 'manual'
      });

      var displayFeatureInfo = function(pixel) {
        info.css({
          left: pixel[0] + 'px',
		  top: (pixel[1] + 60) + 'px'
          //top: (pixel[1] - 15) + 'px'
        });
        var feature = map.forEachFeatureAtPixel(pixel, function(feature) {
          return feature;
        });
        if (feature) {
          info.tooltip('hide')
              .attr('data-original-title', feature.get('name'))
              //.tooltip('fixTitle')
              .tooltip('show');
        } else {
          info.tooltip('hide');
        }
      };

      map.on('pointermove', function(evt) {
        if (evt.dragging) {
          info.tooltip('hide');
          return;
        }
        displayFeatureInfo(map.getEventPixel(evt.originalEvent));
      });

      map.on('click', function(evt) {
        displayFeatureInfo(evt.pixel);
      });


//  Stuff for pop-up below here:

      var element = document.getElementById('popup');

      var popup = new ol.Overlay({
        element: element,
        positioning: 'bottom-center',
        stopEvent: false
      });
      map.addOverlay(popup);

      // display popup on click
      map.on('click', function(evt) {
        var feature = map.forEachFeatureAtPixel(evt.pixel,
            function(feature) {
              return feature;
            });
       // document.getElementById('graphs').innerHTML = "";
        if (feature) {
          var coordinates = feature.getGeometry().getCoordinates();
          popup.setPosition(coordinates);
          $(element).popover({
            'placement': 'top',
            'html': true,
            'content': feature.get('description')
          });

          $(element).popover('show');
        } else {
          $(element).popover('destroy');
        }
      });

// change mouse cursor when over marker
      map.on('pointermove', function(e) {
        if (e.dragging) {
          $(element).popover('destroy');
          return;
        }
        var pixel = map.getEventPixel(e.originalEvent);
        var hit = map.hasFeatureAtPixel(pixel);
        map.getTarget().style.cursor = hit ? 'pointer' : '';
      });

</script>