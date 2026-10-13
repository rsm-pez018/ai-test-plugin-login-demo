import {
    BrowserRouter,
    Routes,
    Route
} from "react-router-dom";


import Register from "./Register";
import Login from "./Login";
import Success from "./Success";


function App() {


    return (

        <BrowserRouter>

            <Routes>


                <Route
                    path="/register"
                    element={<Register />}
                />


                <Route
                    path="/login"
                    element={<Login />}
                />


                <Route
                    path="/success"
                    element={<Success />}
                />


                <Route
                    path="/"
                    element={<Login />}
                />


            </Routes>


        </BrowserRouter>

    );


}


export default App;