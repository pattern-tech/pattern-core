import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Copy, Trash2 } from "lucide-react";

const keys = [
  {
    // name: "Production API Key",
    key: "pk_live_123...",
    created: "2024-11-28",
    lastUsed: "2024-12-02",
  },
  // {
  //   name: "Development API Key",
  //   key: "pk_test_456...",
  //   created: "2024-01-10",
  //   lastUsed: "2024-01-19",
  // },
];

export function ManageKeysPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Gateway ID</CardTitle>
        <CardDescription>
          Your unique identifier to connect with the network.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              {/* <TableHead>Name</TableHead> */}
              <TableHead>Key</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Last Used</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {keys.map((key) => (
              <TableRow key={key.key}>
                {/* <TableCell>{key.name}</TableCell> */}
                <TableCell>{key.key}</TableCell>
                <TableCell>{key.created}</TableCell>
                <TableCell>{key.lastUsed}</TableCell>
                <TableCell>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="icon">
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
