import {
    BrowserRouter,
    Routes,
    Route,
    Navigate
} from "react-router-dom";


import Register from "./Register";
import Login from "./Login";
import Success from "./Success";


function App() {

    return (

        <BrowserRouter>

            <Routes>
                <Route
                    path="/"
                    element={<Navigate to="/register" replace />}
                />

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

            </Routes>

        </BrowserRouter>

    );

}


export default App;
