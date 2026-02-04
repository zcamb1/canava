import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const tdCustomComponents = {
  p: ({ node, ...props }) => (
    <p className="my-2 font-inter">{props.children}</p>
  ),

  // Styles ordered lists
  ol: ({ node, ...props }) => (
    <ol className="my-2 list-decimal list-inside">{props.children}</ol>
  ),

  // Styles unordered lists
  ul: ({ node, ...props }) => (
    <ul className="my-2 list-disc list-inside">{props.children}</ul>
  ),

  // Styles list items
  li: ({ node, ...props }) => <li className="my-1">{props.children}</li>,

  // Styles links to be colored and have a hover effect
  a: ({ node, ...props }) => (
    <a {...props} className="text-blue-600 hover:underline" />
  ),

  br: ({ node, ...props }) => <br />,
};

export const customComponents = {
  table: ({ node, ...props }) => (
    <div className="overflow-x-auto my-4">
      <table className="w-full border-collapse">{props.children}</table>
    </div>
  ),
  thead: ({ node, ...props }) => (
    <thead className="bg-gray-100 dark:bg-gray-700">{props.children}</thead>
  ),
  th: ({ node, ...props }) => (
    <th className="p-2 border border-gray-300 dark:border-gray-600 text-left font-semibold whitespace-nowrap">
      {props.children}
    </th>
  ),
  td: ({ node, ...props }) => {
    const rawMarkdown = node.children.reduce((acc, child) => {
      // The "text" node type contains the raw string
      if (child.type === "text") {
        return acc + child.value;
      }
      // Handle elements like paragraphs or lists
      if (child.children) {
        // Recursively extract text from complex children
        const childText = child.children.map((c) => c.value || "").join("");
        return acc + childText;
      }
      return acc;
    }, "");

    return (
      <td className="p-2 border border-gray-300 dark:border-gray-600 align-top text-[16px]">
        <ReactMarkdown
          components={tdCustomComponents}
          remarkPlugins={[remarkGfm]}
        >
          {rawMarkdown}
        </ReactMarkdown>
      </td>
    );
  },
};

export const ThinkingProcess = ({ content, isOpen, onToggle }) => {
  const contentRef = useRef(null);
  const [maxHeight, setMaxHeight] = useState("0px");
  const [currentOpacity, setCurrentOpacity] = useState(0);

  useEffect(() => {
    // console.log(
    //   `ThinkingProcess [${content.substring(
    //     0,
    //     Math.min(content.length, 20)
    //   )}...]: isOpen prop changed to ${isOpen}`
    // );
    if (contentRef.current) {
      if (isOpen) {
        requestAnimationFrame(() => {
          if (contentRef.current) {
            const scrollHeight = contentRef.current.scrollHeight;
            setMaxHeight(`${scrollHeight}px`);
            setCurrentOpacity(1);
            // console.log(
            //   `ThinkingProcess [${content.substring(
            //     0,
            //     Math.min(content.length, 20)
            //   )}...]: Setting maxHeight to ${scrollHeight}px (open)`
            // );
          }
        });
      } else {
        setMaxHeight(`${contentRef.current.scrollHeight}px`);
        requestAnimationFrame(() => {
          if (contentRef.current) {
            setMaxHeight("0px");
            setCurrentOpacity(0);
            // console.log(
            //   `ThinkingProcess [${content.substring(
            //     0,
            //     Math.min(content.length, 20)
            //   )}...]: Setting maxHeight to 0px (close)`
            // );
          }
        });
      }
    }
  }, [isOpen, content]);

  return (
    // Adjusted margin-top to bring it closer to the bot's icon
    <div className="mt-2 mb-0 flex items-center">
      <div className="group flex-grow">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            e.preventDefault();
            onToggle();
          }}
          // Updated button styling: bg-white
          className="flex items-center cursor-pointer text-gray-700 font-medium bg-white rounded-full pl-4 pr-2 py-2 w-30 h-8 hover:bg-gray-200 transition-all duration-400 ease-in-out focus:outline-none z-0 relative"
        >
          <span className="flex items-center text-sm whitespace-nowrap">
            {/* Removed the thinking icon SVG */}
            Show thinking
          </span>
          <svg
            className={`w-4 h-4 text-gray-600 transform ${
              isOpen ? "rotate-180" : ""
            } transition-transform duration-200 ml-2`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M19 9l-7 7-7-7"
            ></path>
          </svg>
        </button>

        <div
          ref={contentRef}
          // Updated content styling: bg-white
          // className="ml-4 mt-0 text-gray-700 font-inter text-base leading-relaxed bg-white p-1 overflow-hidden transition-all duration-500 ease-in-out border-l-2 border-gray-300 pl-6"
          className="ml-4 mt-0 bg-white p-1 overflow-hidden transition-all duration-500 ease-in-out border-l-2 border-gray-300 pl-6"
          style={{ maxHeight: maxHeight, opacity: currentOpacity }}
        >
          <div className="prose prose-base max-w-none text-gray-800 [&>p]:my-2 [&>ul]:my-2 [&>ol]:my-2 [&>li]:my-1">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={customComponents}
            >
              {content || "Thinking..."}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
};
