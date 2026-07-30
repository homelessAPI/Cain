import { useContext, useEffect, useState } from "react";
import Navbar from "../components/Navbar"
import "./Review.css";
import { GithubContext   } from "../components/GithubContext.jsx";

function Review(){

    const [loading, setLoading] = useState(true)

    const {

    username,

    user,

    events,

    repos,

    languages,

    weekday,

    review

} = useContext(GithubContext  );

    useEffect(() => {
        async function getReview() {

            try {

            const response = await fetch(`${import.meta.env.VITE_API_URL}/review`,
            {
                method: 'POST',
                headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify({username:username})
            }
            )

            const data = await response.json();


            setLoading(false)
            setReview(data.AI_Review);
            }
            catch (err){
                setReview("Failed to fetch Review")
            }

            finally {
                setLoading(false)
            }

        }
        getReview();

    }, []);



return (
    <>

    <Navbar />

    <div className="ai_review">
        <h1>AI Review</h1>
        {loading ? <p>...Analysing profile...</p> : <p>{review}</p>}
    </div>
    </>
)

}


export default Review;