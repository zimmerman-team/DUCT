/**
 * Created by billy on 5/18/16.
 */
var dataSet, varnames, varlabs, vallabs, selectX, selectY, graphVarNames, selected, ddid, list;
var margin = {top: 20, right: 20, bottom: 30, left: 80},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

d3.json("/static/data/msas.json", function(error, data) {
    if (error) throw error;
    dataSet = data.data.data;
    varnames = data.variableNames;
    varlabs = d3.map(data.variableLabels);
    vallabs = d3.map(data.valueLabels);
    graphVarNames = varnames.filter(function(d) { return !data.variableIsString[d]; });
    var control = d3.select("body").append("div").attr("id", "controls");
    selectY = control.append("span")
        .attr("class", "col-xs-12 col-sm-offset-1 col-sm-3")
        .attr("id", "yvspan")
        .text("Y-Axis Variable : ")
        .append("select")
        .attr("id", "yvar")
        .attr("onchange", "scatter()");

    selectY.selectAll("option")
        .data(graphVarNames)
        .enter().append("option")
        .attr("value", function(d) { return d; })
        .text(function(d) { return varlabs.get(d); });

    selectX = control.append("span")
        .attr("class", "col-xs-12 col-sm-3")
        .text("X-Axis Variable : ")
        .append("select")
        .attr("id", "xvar")
        .attr("onchange", "scatter()");

    selectX.selectAll("option")
        .data(graphVarNames)
        .enter().append("option")
        .attr("value", function(d) { return d; })
        .text(function(d) { return varlabs.get(d); });

    scatter();
});

function scatter() {

    d3.select("div#graphArea").remove(),
    d3.select(".dataTables_wrapper").remove(),
    d3.select("div#vdtab").remove(),
    d3.select(".tooltip").remove();
    var svg = d3.selectAll("svg"),
        group = "mic";

    svg.remove();
    var xvar = d3.select("select#xvar").property("value"),
        yvar = d3.select("select#yvar").property("value");

    dataSet.forEach(function(d) {
        d[xvar] = +d[xvar];
        d[yvar] = +d[yvar];
    });

    var xValue = function(d) { if (!isNaN(d[xvar]) && d[xvar] !== null) return d[xvar];}, // data -> value
        xScale = d3.scale.linear().range([0, width]), // value -> display
        xMap = function(d) { return xScale(xValue(d));}, // data -> display
        xAxis = d3.svg.axis().scale(xScale).orient("bottom"),
        yValue = function(d) { if (!isNaN(d[yvar]) && d[yvar] !== null) return d[yvar];}, // data -> value
        yScale = d3.scale.linear().range([height, 0]), // value -> display
        yMap = function(d) { return yScale(yValue(d));}, // data -> display
        yAxis = d3.svg.axis().scale(yScale).orient("left"),
        gdata = dataSet.filter(function(d) { if (!isNaN(d[xvar]) && !isNaN(d[yvar])) {
            return d;
        }
        });

    xScale.domain([d3.min(dataSet, xValue) - 1, d3.max(dataSet, xValue) + 1]);
    yScale.domain([d3.min(dataSet, yValue) - 1, d3.max(dataSet, yValue) + 1]);

    var cValue = function(d) { return d[group]; },
        color = d3.scale.category10();

    // add the graph canvas to the body of the webpage
    svg = d3.select("body").append("div").attr("class", "col-sm-offset-1 col-sm-8").attr("id", "graphArea").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    d3.select("body").append("div").attr("id", "vdtab").attr("class", "col-sm-offset-1 col-sm-8");
    var header = [ 'Vizualization Data' ],
        para = [ 'You can also browse all of the data currently being used in the graph above with this table.  Click on any of the buttons at the top of the table to remove/show those columns, click on the column headers to sort the data, or enter terms to search for across all the fields in the data in the text box at the top.  You can also adjust the number of rows by clicking on the dropdown menu above the table and on the left side of the page.' ],
        h1 = d3.select("div#vdtab").selectAll("h1").data(header),
        vtpara = d3.select("div#vdtab").selectAll("p").data(para);
    h1.enter().append("h1").text(function(d) { return d; });
    vtpara.enter().append("p").text(function(d) { return d; });

    var tooltip = d3.select("body").append("div")
                    .attr("class", "tooltip");

    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .attr("class", "label")
        .attr("x", width)
        .attr("y", -6)
        .style("text-anchor", "end")
        .text(function() { return varlabs.get(xvar); });

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("class", "label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(function() { return varlabs.get(yvar); });

    svg.selectAll(".dot")
        .data(gdata)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("r", 3.5)
        .attr("cx", xMap)
        .attr("cy", yMap)
        .style("fill", function(d) { return color(cValue(d));})
        .on("mouseover", function(d) {
            tooltip.transition()
                .duration(200)
                .style({ "opacity": .9, "visible" : true });
            tooltip.html(d["country"] + '&nbsp;&nbsp; - &nbsp;&nbsp;' + d["schnm"] + "<br/>" +
                varlabs.get(xvar) + " = " + xValue(d) + '<br/>' +
                varlabs.get(yvar) + " = " + yValue(d))
                .style("left", (d3.event.pageX + 5) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function(d) {
            tooltip.transition()
                .duration(500)
                .style({ "opacity": 0, "visible": "hidden" });
        });


    var legend = svg.selectAll(".legend")
        .data(color.domain())
        .enter().append("g")
        .attr("class", "legend")
        .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

    // draw legend colored rectangles
    legend.append("rect")
        .attr("x", width - 18)
        .attr("width", 18)
        .attr("height", 18)
        .style("fill", color);

    // draw legend text
    legend.append("text")
        .attr("x", width - 24)
        .attr("y", 9)
        .attr("dy", ".35em")
        .style("text-anchor", "end")
        .text(function(d) { return vallabs.get(group)[d];});

    var table_plot = makeTable()
        .datum(gdata)
        .filterCols(graphVarNames.filter(function(d) {
            if (d !== xvar && d !== yvar) return d;
        }));

    d3.select("body").call(table_plot);

    table_plot.on('highlight', function(data, on_off){
        if(on_off){//if the data is highlighted
            d3.select('#highlighted');
        }
    });
    table_plot.on('select', function(data, on_off){
        if(on_off){//if the data is highlighted
            d3.select('#selected');
        }
    });

//    d3.select("div#vizData_wrapper").attr("class", "col-sm-offset-1 col-sm-8").append("div").attr("class", "col-sm-offset-3");
//    d3.select("table#vizData").style("width", "100%");
}

function selectedVars(id) {

        selected = d3.map({"yvar" : d3.select("#yvar").property("value"), "xvar" : d3.select("#xvar").property("value") });
        if (selected.get("yvar") === selected.get("xvar")) {
            d3.select("#xvar option[value='" + selected.get("yvar") + "']").remove();
        }
        selected = d3.map({"yvar" : d3.select("#yvar").property("value"), "xvar" : d3.select("#xvar").property("value") }),
            ddid = selected.keys().filter(function(d) { if (d !== id) return true; }),
            lists = {"yvar" : graphVarNames.filter(function(d) { return d !== selected.get("xvar"); }),
                    "xvar" : graphVarNames.filter(function(d) { return d !== selected.get("yvar"); }) };
        return {"selected" : selected, "ddid" : ddid, "lists" : lists };
}

function xLoad() {

    // d3.select("select#xvar").selectAll("option").remove();

    var listData = selectedVars("xvar"),
        xdd = d3.select("select#xvar")
                .selectAll("option")
                .data(listData.lists.xvar);

    xdd.enter().append("option")
        .attr("value", function(d) { return d; })
        .text(function(d) { return varlabs.get(d); });

    xdd.exit().remove();

    scatter();

}

function xChange() {
    var varlist = selectedVars("xvar"),
        xrem = varlist.selected.get("yvar"),
        yrem = varlist.selected.get("xvar"),
        xv = d3.select("#xvar").selectAll("option"),
        yv = d3.select("#yvar").selectAll("option");
    yv.data(xrem).exit().remove();


    scatter();

}




