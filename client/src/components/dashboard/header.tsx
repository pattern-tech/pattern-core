import { useLocation, Link } from "react-router-dom";
import { Slash } from "lucide-react";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import React from "react";


export function Header() {
  const location = useLocation();

  // Split the current location pathname into segments
  const pathSegments = location.pathname.split("/").filter((segment) => segment);

  const breadcrumbItems = pathSegments.map((segment, index) => {
    const path = `/${pathSegments.slice(0, index + 1).join("/")}`;
    return { label: segment, path };
  });

  return (
    <div className="border-b">
      <div className="flex flex-col space-y-2 px-4 py-2">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <Link to="/" className="breadcrumb-link">
                Home
              </Link>
            </BreadcrumbItem>
            {breadcrumbItems.map((item) => (
              <React.Fragment key={item.path}>
                <BreadcrumbSeparator>
                  <Slash />
                </BreadcrumbSeparator>
                <BreadcrumbItem>
                  <Link to={item.path} className="breadcrumb-link">
                    {item.label.charAt(0).toUpperCase() + item.label.slice(1)}
                  </Link>
                </BreadcrumbItem>
              </React.Fragment>
            ))}
          </BreadcrumbList>
        </Breadcrumb>
      </div>
    </div>
  );
}
