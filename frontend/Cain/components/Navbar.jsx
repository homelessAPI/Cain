import { Link } from "react-router-dom";
import "./Navbar.css";

function Navbar(){
    return(
        <nav className="Navbar">
            <h1>CAIN</h1>
            <div className="Links">
                <Link className="Link" to="/" >Home </Link>
                <Link className="Link" to="/review" >Review </Link>
            </div>

        </nav>
    )
}

export default Navbar;