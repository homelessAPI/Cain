import { useContext, useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import ReactMarkdown from "react-markdown";
import "./Review.css";
import { GithubContext } from "../components/GithubContext.jsx";


function Review(){

    const [loading, setLoading] = useState(true);


    const {
        username,
        review,
        setReview
    } = useContext(GithubContext);



    useEffect(() => {

        if (!username) {
            setReview("No GitHub username found.");
            setLoading(false);
            return;
        }


        async function getReview(){

            setLoading(true);
            setReview("");

            try {

                const response = await fetch(
                    `${import.meta.env.VITE_API_URL}/review`,
                    {
                        method:"POST",
                        headers:{
                            "Content-Type":"application/json"
                        },
                        body:JSON.stringify({
                            username:username
                        })
                    }
                );


                if (!response.ok || !response.body){
                    throw new Error("Failed request");
                }


                const reader = response.body.getReader();

                const decoder = new TextDecoder();

                let fullText = "";


                while(true){

                    const {
                        done,
                        value
                    } = await reader.read();


                    if(done) break;


                    const chunk = decoder.decode(
                        value,
                        {
                            stream:true
                        }
                    );


                    fullText += chunk;


                    setReview(fullText);


                    setLoading(false);
                }


            }
            catch(error){

                console.error(error);

                setReview(
                    "Failed to generate review."
                );

                setLoading(false);
            }

        }


        getReview();


    }, [username]);



    return(
        <>
            <Navbar/>

            <div className="ai_review">

                <h1>
                    AI Review: {username}
                </h1>


                <h3>
                    Please be patient, my Lenovo is fighting for its life.
                </h3>


                {
                    loading
                    ?
                    <p>
                        ...Analysing profile...
                    </p>
                    :
                    <ReactMarkdown>
                        {review}
                    </ReactMarkdown>
                }

            </div>

        </>
    )
}


export default Review;