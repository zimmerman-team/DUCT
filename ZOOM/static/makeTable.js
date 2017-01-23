/**
 * Copied from http://bl.ocks.org/ahmohamed/4c4980f31abdef64e7e2 with minor modifications
 */
var columnArg, table;

function makeTable() {

    var data, sort_by, filter_cols; // Customizable variables

    // var table; // A reference to the main DataTable object

    // This is a custom event dispatcher.
    var dispatcher = d3.dispatch('highlight', 'select');

    $.extend( true, $.fn.dataTable.defaults, {
        "searching": true,
        "ordering": true
    } );

    // Main function, where the actual plotting takes place.
    function _table() {

        // Create and select table skeleton
        var tableSelect = d3.select("body").append("table")
                    .attr("class", "display")
        // Generally, hard-coding Ids is wrong, because then 
        // you can't have 2 table plots in one page (both will have the same id).
        // I will leave it for now for simplicity. TODO: remove hard-coded id.
            .attr("id", "vizData")
            .style("visibility", "hidden"); // Hide table until style loads;

        // Set column names
        var colnames = Object.keys(data[0]);
        if(typeof filter_cols !== 'undefined'){
            // If we have filtered cols, remove them.
            colnames = colnames.filter(function (e) {
                // An index of -1 indicate an element is not in the array.
                // If the col_name can't be found in the filter_col array, retain it.
                return filter_cols.indexOf(e) < 0;
            });
        }

        if(typeof sort_by !== 'undefined'){
            // if we have a sort_by column, format it according to datatables.
            sort_by[0] = colnames.indexOf(sort_by[0]); //colname to col idx
            sort_by = [sort_by]; //wrap it in an array
        }

        columnArg = [];
        colnames.forEach(function(d) {
            columnArg.push({"title": varlabs.get(d), "data": d, "searchable": true});
        });

        //console.log(columnArg);

        // Apply DataTable formatting: https://www.datatables.net/
        $(document).ready(function() {

            table = $("#vizData").DataTable({
                // Here, I am supplying DataTable with the data to fill the table.
                // This is more efficient than supplying an already contructed table.
                // Refer to http://datatables.net/manual/data#Objects for details.
                "dom": '<"col-sm-offset-1 col-sm-8"lBftip>',
                data: data,
                columns: columnArg,
                deferRender: true,
                "pagingType": "full_numbers",
                paging: true,
                order: sort_by,
                lengthMenu: [[5, 10, 25, 50, 100, -1], [5, 10, 25, 50, 100, "All"]],
                buttons: [ 'columnsToggle' ],
                select: true
            });

            $("#vizData tbody")
                .on( 'mouseover', 'tr', function () { highlight(this, true); } )
                .on( 'mouseleave', 'tr', function () { highlight(this, false); } )
                .on('click', 'tr', function () { select(this); });

        });

        d3.select("div#vizData_wrapper").attr("class", "dataTables_wrapper");
        // Make the table visible
        tableSelect.style("visibility", "visible");

    }

    /**** Helper functions to highlight and select data **************/
    function highlight(row, on_off) {
        if(typeof on_off === 'undefined'){
            // if on_off is not provided, just toggle class.
            on_off = !d3.select(row).classed('highlight');
        }
        // Set the row's class as highlighted if on==true,
        // Otherwise remove the 'highlighted' class attribute.
        // In DataTables, this is handled automatically for us.
        d3.select(row).classed('highlight', on_off);

        // Fire a highlight event, with the data and highlight status.
        dispatcher.highlight(table.rows(row).data()[0], on_off);
    }
    function select(row, on_off) {
        // Similar to highlight function.
        if(typeof on_off === 'undefined'){
            on_off = !d3.select(row).classed('selected');
        }

        d3.select(row).classed('selected', on_off);

        // Fire a select event, with the data and selected status.
        dispatcher.select(table.rows(row).data()[0], on_off);
    }

    /**** Setter / getters functions to customize the table plot *****/
    _table.datum = function(_){
        if (!arguments.length) {return data;}
        data = _;

        return _table;
    };
    _table.filterCols = function(_){
        if (!arguments.length) {return filter_cols;}
        filter_cols = _;

        return _table;
    };
    _table.sortBy = function(colname, ascending){
        if (!arguments.length) {return sort_by;}

        sort_by = [];
        sort_by[0] = colname;
        sort_by[1] = ascending ? 'asc': 'desc';

        return _table;
    };

    // This allows other objects to 'listen' to events dispatched by the _table object.
    d3.rebind(_table, dispatcher, 'on');

    // This is the return of the main function 'makeTable'
    return _table;
}
