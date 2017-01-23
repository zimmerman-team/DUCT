/**
 * Function to convert array of JSON Objects into two dimensional associative array.
 * This should make it easier to translate some D3js examples when working with JSON data produced by the jsonio program
 * in Stata.
 * @param jsonData An array of JSON Objects representing records from a 2-D structure
 * @param toNumeric A boolean indicating whether or not the function should attempt to convert string literals to numeric values if possible
 * @param stdMissing A boolean indicating whether string literal "null" values should be replace with null values
 * @return A two dimensional associative array containing key-value pairs for each of the properties of the JSON object
 */

// Defines the function jsonToArray
function jsonToArray(jsonData, toNumeric, stdMissing) {

    // Defines a variable used to store the returned result
    var arrayData = [];

    // Loop over the objects in the data.data.data object from the jsonio output or other similarly structured data (an Array of JSON objects)
    for (var i = 0; i < jsonData.length; i++) {

        // Stores an individual object from the array and declares container used by inner loop to transform the
        // JSON object to a rowvector
        var ob = jsonData[i],
            row = [];

        // Loops over the properties (variables/columns) in the JSON object
        for (var j in ob) {

            // Declares container used to store the value from the property
            var val;

            // If user wants standardized missing values and to force conversion to numeric values
            if (stdMissing && toNumeric) {

                // If the value is a number make sure the datum is cast as a number
                if (!isNaN(ob[j])) val = +ob[j];

                // If value is not a number and contains string literal null, replace the value with null
                else if(isNaN(ob[j]) && ob[j] == "null") val = null;

                // Otherwise return the original value (should be a string)
                else val = ob[j];

            // If the user only wants to standardize missing values
            } else if (stdMissing && !toNumeric) {

                // If the value is a string literal "null" value replace it with null
                if (ob[j] === "null") val = null;

                // Otherwise return the original value
                else val = ob[j];

            // If the user only wants to recast values to numeric if they are numeric values
            } else if (!stdMissing && toNumeric) {

                // If the value is a number force casting to numeric
                if (!isNaN(ob[j])) val = +ob[j];

                // Or return the original value
                else val = ob[j];

            // For all other cases
            } else {

                // Return the original value
                val = ob[j];

            } // End the ELSE Block for the stdMissing and toNumeric options

            // Create a new key : value pair object for the value of this variable for the record
            var datum = { [j] : val };

            // Add this variable to the "row"/record array
            row.push(datum);

        } // End Loop over the properties in the object

        // Add this record to the array container
        arrayData.push(row);

    } // End Loop over the objects

    // Return the 2-D array
    return arrayData;

} // End of Function declaration


/**
 * Function to access column from 2-D Array
 * Copied from: http://stackoverflow.com/questions/7848004/get-column-from-a-two-dimensional-array-in-javascript
 * Code provided by user Gothdo.
 * @param arr The 2D JavaScript Array
 * @param n The Column to access
 * @returns A 1D array containing the values for the given column
 */
function getColumn(arr, n) {
    return arr.map(x => x[n]);
};

/**
 * Function used to access values from JSON data
 * @param json The JSON object from which the data should be retrieved
 * @param col The variable/column to retrieve from the objects
 * @param removeNull Option to remove string literal nulls 
 * @returns A 1D array of values 
 */
function getColumnFromJSON(json, col, removeNull) {
    if (removeNull) {
        return json.map(x => x[col]).filter(function(d) {
        if (d !== "null" && d !== null) return true;
        else return false; 
        });
    } else {
        return json.map(x => x[col]);
    }
}