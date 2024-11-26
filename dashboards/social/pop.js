import { TableauViz } from "https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.js";
 
// Variables for controling the functionality. 
const vizURL = "https://public.tableau.com/views/Penangspopulationanddemographics/Overalltrend"
const widthThreshold   = 600;                  // Threshold at which we'll swtich from phont to desktop or vice versa.
const fitBrowserPhone  = true;                 // On phone layout, should the width expand to the browser or use a set width.
const desktopWidth     = '1000px';             // Width for desktop layout.
const desktopHeight    = '850px';             // Height for desktop layout. Add 27px for padding.
const phoneWidth       = '375px';              // Width for phone layout (if we are not auto-fitting to the browser).
const phoneHeight      = '1450px';              // Height for the phone layout.
const toolbarPosition  = "bottom"              // Position of the toolbar. Options are bottom, top, hidden. Hidden not available on Tableau Public

const viz = new TableauViz();

viz.src = vizURL;
viz.toolbar = toolbarPosition;

// // Check screen width and choose appropriate widths to display.
if (window.innerWidth > widthThreshold)
  {
  // Desktop Layout
  viz.device='desktop';
  viz.height=desktopHeight;
  viz.width=desktopWidth;
  }
else
  {
  // Phone Layout
  viz.device='phone';
  viz.height=phoneHeight;
  viz.hideTabs = true;

  if (fitBrowserPhone == true)
    {
    // Set to the browser width-27 (avoids horizontal scrolling).
     viz.width = window.innerWidth-27;
    }
  else
    {
    // Set to the static phone layout width.
    viz.width = phoneWidth;
    }         
  }

// // Set the div dimensions to that of the viz in case scrolling is needed.
document.getElementById('tableauViz').style.width=viz.width;
document.getElementById('tableauViz').style.height=viz.height;
      
document.getElementById("tableauViz").appendChild(viz);
