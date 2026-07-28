import { useEffect, useState } from "react";
import Navbar from "../components/Navbar"
import "./Review.css";


function Review(){

    const [review, setReview] = useState("")
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        async function getReview() {

            const username = localStorage.getItem("Github_Username");

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
        {loading ? <p>Analysing profile</p> : <p>{review}</p>}
    </div>
    </>
)

}


export default Review;