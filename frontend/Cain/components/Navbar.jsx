import { Link } from "react-router-dom";
import "./Navbar.css";

function Navbar(){
    return(
        <div className="NavbarContainer">
            <nav className="Navbar">
            <h1>CAIN</h1>
            <div className="LinksContainer">
                <Link className="Link" to="/" >Home </Link>
            </div>

        </nav>
        </div>
    )
}

export default Navbar;