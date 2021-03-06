import React from "react";
import {Navbar} from "react-bootstrap";

const Footer = props => {
    return (
        <div>
            <Navbar
                className={"bottom mt-5 flex-column"}
            >
                <p className={"flex-row"}>
                    Contribute or clone this website <a href="https://github.com/weee-open/softweeere" target="_blank" rel="nofollow noopener noreferrer">here</a>!
                </p>
                <p className={"flex-row text-center"}>
                    Follow us on
                    <a href="http://weeeopen.polito.it" target="_blank" rel="nofollow noopener noreferrer"> our website</a>
                    ,
                    <a href="https://www.facebook.com/weeeopen/" target="_blank" rel="nofollow noopener noreferrer"> Facebook</a>
                    ,
                    <a href="https://www.instagram.com/weeeopen/" target="_blank" rel="nofollow noopener noreferrer"> Instagram</a>
                    ,
                    <a href="https://www.linkedin.com/company/weee-open/" target="_blank" rel="nofollow noopener noreferrer"> LinkedIn </a>
                    and on
                    <a href="https://politecnico-di-torino.hivebrite.com/topics/9837/" target="_blank" rel="nofollow noopener noreferrer"> PoliTOnet</a>.
                </p>
                <p>
                    Licensing found <a href={"https://github.com/weee-open/softweeere#licensing"} target="_blank" rel="nofollow noopener noreferrer">here</a>.
                </p>
            </Navbar>
        </div>
    );
}

export default Footer;