import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const activities = [
  {
    user: {
      name: "Sarah Miller",
      image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100",
      initials: "SM"
    },
    action: "Created a new project",
    time: "2 minutes ago"
  },
  {
    user: {
      name: "David Chen",
      image: "https://images.unsplash.com/photo-1599566150163-29194dcaad36?w=100",
      initials: "DC"
    },
    action: "Completed task review",
    time: "1 hour ago"
  },
  {
    user: {
      name: "Alex Thompson",
      image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100",
      initials: "AT"
    },
    action: "Updated documentation",
    time: "3 hours ago"
  }
];

export function RecentActivity() {
  return (
    <Card className="col-span-3">
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest actions from your team</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-8">
          {activities.map((activity, index) => (
            <div key={index} className="flex items-center">
              <Avatar className="h-9 w-9">
                <AvatarImage src={activity.user.image} alt={activity.user.name} />
                <AvatarFallback>{activity.user.initials}</AvatarFallback>
              </Avatar>
              <div className="ml-4 space-y-1">
                <p className="text-sm font-medium leading-none">
                  {activity.user.name}
                </p>
                <p className="text-sm text-muted-foreground">
                  {activity.action}
                </p>
              </div>
              <div className="ml-auto text-sm text-muted-foreground">
                {activity.time}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}