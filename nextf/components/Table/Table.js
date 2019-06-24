import React from 'react';
import ReactTable from "react-table";
import Moment from 'moment';
import "react-table/react-table.css";

class Table extends React.Component {
  render() {
    const { data, header } = this.props;
    const columns = header.map(
      (col) => {
        const thead = { Header: col, accessor: col };
        if (col === 'DateTime') {
          thead.accessor = d => {
            return Moment(d['DateTime'])
              .local()
              .format("DD-MM-YYYY hh:mm:ss a")
          };
          thead.id = 'DateTime';
        }
        return thead;
      }
    );
    return (
      <ReactTable
        data={data}
        columns={columns}
        defaultPageSize={10}
        className="-striped -highlight"
      />
    );
  }
}

export default Table;
