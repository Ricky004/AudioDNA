"use client"

import Microphone from "./Microphone";
import SongUploader from "./SongUploader";

const MainComponent = () => {
    return (
        <div className="flex flex-col justify-center items-center h-screen gap-10 bg-gray-900 text-white">
            <Microphone />
            <SongUploader />
        </div>
    );
};

export default MainComponent;