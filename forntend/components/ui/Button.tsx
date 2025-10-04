import { ButtonHTMLAttributes } from "react";
import { clsx } from "clsx";

export default function Button({
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={clsx(
        "px-4 py-2 rounded-md bg-indigo-600 text-white hover:bg-indigo-700 transition",
        className
      )}
      {...props}
    />
  );
}