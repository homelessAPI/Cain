import { useContext, useEffect, useState } from "react";
import Navbar from "../components/Navbar"
import ReactMarkdown from "react-markdown";
import "./Review.css";
import { GithubContext } from "../components/GithubContext.jsx";

function Review(){

    const [loading, setLoading] = useState(true)

    const {

    username,

    user,

    events,

    repos,

    languages,

    weekday,

    review,

    setReview

} = useContext(GithubContext);

    useEffect(() => {
        async function getReview() {

            const username = localStorage.getItem("Github_Username");

            if (!username) {
                setReview("No GitHub username found.");
                setLoading(false);
                return;
            }

            try {

                const response = await fetch(`${import.meta.env.VITE_API_URL}/review`,
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ username: username })
                    }
                )

                if (!response.ok || !response.body) {
                    setReview("Failed to fetch Review")
                    return
                }

                // Once the first chunk arrives, stop showing the loading state
                // and start rendering text as it streams in.
                setLoading(false)

                const reader = response.body.getReader()
                const decoder = new TextDecoder()
                let fullText = ""

                while (true) {
                    const { done, value } = await reader.read()
                    if (done) break

                    const chunkText = decoder.decode(value, { stream: true })
                    fullText += chunkText
                    setReview(fullText)
                }
            }
            catch (err) {
                console.error(err)
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
        <h1>AI Review: {username}</h1>
        <h3>Please be paitent as i do not own a data center but an overworked lenovo laptop</h3>
        {loading ? <p>...Analysing profile...</p> : <ReactMarkdown>{review}</ReactMarkdown>}
    </div>
    </>
)

}


export default Review;