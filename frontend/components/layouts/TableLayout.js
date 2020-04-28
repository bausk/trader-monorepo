import React from 'react';
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";


function Layout({ children, toolbar, title }) {
  return (
    <>
        <h1>{title}</h1>
        <div>
            <AppBar position="static">
                <Toolbar>
                    {toolbar()}
                </Toolbar>
            </AppBar>
            {children}
        </div>
    </>
  )
}

export default Layout;
