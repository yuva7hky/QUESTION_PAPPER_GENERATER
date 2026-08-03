/**
 * Header Component
 * 
 * Full-width top banner image + application title header.
 * Banner image spans almost the full page width without cropping.
 */
export default function Header() {
  return (
    <header className="w-full bg-white shadow-sm border-b border-gray-200 py-4 px-4 sm:px-8 mb-6">
      <div className="max-w-7xl mx-auto flex flex-col items-center">
        {/* Full-Width College Banner Image */}
        <div className="w-full max-w-5xl rounded-xl overflow-hidden shadow-xs border border-gray-100 bg-white">
          <img
            src="/college-banner.jpeg"
            alt="College Banner"
            className="w-full h-auto object-contain max-h-[140px]"
          />
        </div>

        {/* Application Title */}
        <div className="mt-4 text-center">
          <h1 className="text-xl sm:text-2xl font-extrabold text-blue-950 tracking-wider">
            QUESTION PAPER GENERATION SYSTEM
          </h1>
          <p className="text-xs text-gray-500 mt-1 font-medium tracking-wide uppercase">
            Examination Cell Management Software
          </p>
        </div>
      </div>
    </header>
  );
}
