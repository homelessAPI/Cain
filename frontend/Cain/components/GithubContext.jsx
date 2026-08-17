import { createContext, useState } from "react";

export const GithubContext = createContext();

export function GithubProvider({ children }) {

    const [username, setUsername] = useState("");

    const [user, setUser] = useState(null);

    const [events, setEvents] = useState([]);

    const [repos, setRepos] = useState([]);

    const [languages, setLanguages] = useState([]);

    const [weekday, setWeekday] = useState({});

    const [review, setReview] = useState("")

    const [quality, setQuality] = useState(null);

    return (

        <GithubContext.Provider
            value={{

                username,
                setUsername,

                user,
                setUser,

                events,
                setEvents,

                repos,
                setRepos,

                languages,
                setLanguages,

                weekday,
                setWeekday,

                review,
                setReview,

                quality,
                setQuality,

            }}
        >

            {children}

        </GithubContext.Provider>

    );

}